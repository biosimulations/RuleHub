from Bio import Entrez
from biosimulators_utils.combine.data_model import CombineArchive, CombineArchiveContent, CombineArchiveContentFormat
from biosimulators_utils.combine.io import CombineArchiveWriter
from biosimulators_utils.config import Config
# from biosimulators_utils.omex_meta.data_model import OmexMetaOutputFormat
from biosimulators_utils.omex_meta.io import BiosimulationsOmexMetaWriter, BiosimulationsOmexMetaReader
# from biosimulators_utils.omex_meta.utils import build_omex_meta_file_for_model
from biosimulators_utils.ref.data_model import Reference, PubMedCentralOpenAccesGraphic  # noqa: F401
from biosimulators_utils.ref.utils import get_reference, get_pubmed_central_open_access_graphics
from biosimulators_utils.sedml.data_model import (
    SedDocument, Model, ModelLanguage, UniformTimeCourseSimulation,
    Task, DataGenerator, Report, DataSet)
from biosimulators_utils.sedml.io import SedmlSimulationWriter
from biosimulators_utils.sedml.model_utils import get_parameters_variables_outputs_for_simulation
from biosimulators_utils.warnings import BioSimulatorsWarning
import biosimulators_bionetgen
import biosimulators_utils.biosimulations.utils
import datetime
import os
import shutil
import tempfile
import yaml

Entrez.email = os.getenv('ENTREZ_EMAIL', None)

__all__ = ['run']


BASE_DIRNAME = os.path.join(os.path.dirname(__file__), '..')


def run(dry_run=False):

    # get list of models
    models = get_models()

    # read import status file
    for i_model, (category, model_name) in enumerate(models):
        model_dirname = os.path.join(BASE_DIRNAME, category, model_name)

        # read metadata
        yml_metadata_filename = os.path.join(model_dirname, 'metadata.yml')
        with open(yml_metadata_filename, 'r') as file:
            metadata = yaml.load(file, Loader=yaml.Loader)

        # skip model if not ready to publish to BioSimulations
        if not metadata.get('biosimulations', {}).get('publish', True):
            continue

        # get additional metadata
        ncbi_taxonomy_id = metadata.get('taxon', {}).get('ncbiTaxonomyId', None)
        if ncbi_taxonomy_id:
            handle = Entrez.esummary(db="taxonomy", id=ncbi_taxonomy_id, retmode="xml")
            record = Entrez.read(handle)
            assert len(record) == 1
            handle.close()

            metadata['taxon']['uri'] = 'http://identifiers.org/taxonomy:{}'.format(ncbi_taxonomy_id)
            metadata['taxon']['label'] = record[0]['ScientificName']

        # Citation information for the associated publication
        for citation in metadata.get('citations', []):
            reference = get_reference(
                pubmed_id=citation.get('pubmedId', None),
                doi=citation.get('doi', None),
            )
            if reference.doi:
                citation['uri'] = 'http://identifiers.org/doi:{}'.format(reference.doi)
            elif reference.pubmed_id:
                citation['uri'] = 'http://identifiers.org/pubmed:{}'.format(reference.pubmed_id)
            citation['label'] = reference.get_citation()

            # Figures for the associated publication from open-access subset of PubMed Central
            if reference.pubmed_central_id:
                thumbnails = get_pubmed_central_open_access_graphics(
                    reference.pubmed_central_id,
                    os.path.join(config['source_thumbnails_dirname'], reference.pubmed_central_id),
                )
            else:
                thumbnails = []

        # get thumbnails
        thumbnail = []
        for thumbnail in os.path.listdir(os.path.join(model_dirname, 'thumbnails')):
            ext = os.path.splitext(thumbnail)
            if ext.lower() in [".gif", ".jpg", ".jpeg", ".png"]:
                thumbnails.append(thumbnail)

        # export metadata to OMEX metadata XML-RDF format
        print('Exporting project metadata for {} of {}: {}'.format(i_model + 1, len(models), model_name))
        rdf_metadata_filename = os.path.join(model_dirname, model_name + '.rdf')
        BiosimulationsOmexMetaWriter().run(metadata, metadata_filename)
        _, errors, warnings = BiosimulationsOmexMetaReader().run(metadata_filename)
        assert not errors

        # create SED-ML simulation from BNGL model file(s)

        # combine model, simulation, metadata, and thumbnail files in COMBINE/OMEX archive
        print('Converting model {} of {}: {} ...'.format(i_model + 1, len(models), model['model_bigg_id']))

        project_filename = os.path.join(model_dirname, 'project.omex')

        extra_contents = {}
        extra_contents[project_metadata_filename] = CombineArchiveContent(
            location='metadata.rdf',
            format=CombineArchiveContentFormat.OMEX_METADATA,
        )
        # extra_contents[model_metadata_filename] = CombineArchiveContent(
        #     location=model['model_bigg_id'] + '.rdf',
        #     format=CombineArchiveContentFormat.OMEX_METADATA,
        # )
        extra_contents[config['source_license_filename']] = CombineArchiveContent(
            location='LICENSE',
            format=CombineArchiveContentFormat.TEXT,
        )
        for escher_map in model['escher_maps']:
            escher_filename = os.path.join(config['source_visualizations_dirname'], escher_map['map_name'] + '.json')
            vega_filename = os.path.join(config['final_visualizations_dirname'], escher_map['map_name'] + '.json')
            extra_contents[escher_filename] = CombineArchiveContent(
                location=escher_map['map_name'] + '.escher.json',
                format=CombineArchiveContentFormat.Escher,
            )
            extra_contents[vega_filename] = CombineArchiveContent(
                location=escher_map['map_name'] + '.vega.json',
                format=CombineArchiveContentFormat.Vega,
            )
        for thumbnail in thumbnails:
            extra_contents[thumbnail.filename] = CombineArchiveContent(
                location=reference.pubmed_central_id + '-' + os.path.basename(thumbnail.id) + '.jpg',
                format=CombineArchiveContentFormat.JPEG,
            )

        build_combine_archive_for_model(model_filename, project_filename, extra_contents=extra_contents)

        # check if archive hasn't changed. if archive hasn't changed, skip simulating it and pushing it to BioSimulations

        # simulate COMBINE/OMEX archives
        print('Simulating model {} of {}: {} ...'.format(i_model + 1, len(models), model_name))

        simulation_outputs_dirname = os.path.join(model_dirname, 'outputs')
        biosimulators_utils_config = Config(COLLECT_COMBINE_ARCHIVE_RESULTS=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", BioSimulatorsWarning)
            results, log = biosimulators_bionetgen.exec_sedml_docs_in_combine_archive(
                project_filename, simulation_outputs_dirname, config=biosimulators_utils_config)

        if log.exception:
            raise log.exception

        duration = log.duration

        # submit COMBINE/OMEX archive to BioSimulations
        if dry_run:
            runbiosimulations_id = None
        else:
            runbiosimulations_id = biosimulators_utils.biosimulations.utils.submit_project_to_runbiosimulations(
                model_name, project_filename, 'bionetgen')

        # output status
        now = str(datetime.datetime.utcnow())
        if 'biosimulations' not in metadata:
            metadata['biosimulations'] = {
                'created': now,
            }
        metadata['biosimulations']['updated'] = now
        metadata['biosimulations']['duration'] = duration,
        metadata['biosimulations']['id'] = runbiosimulations_id
        with open(yml_metadata_filename, 'w') as file:
            file.write(yaml.dump(metadata))


def get_models():
    models = []
    for category in ['Contributed', 'Published']:
        for path in os.listdir(os.path.join(BASE_DIRNAME, category)):
            if os.path.isdir(os.path.join(BASE_DIRNAME, category, path)):
                models.append((category, path))
    return models


def build_combine_archive_for_model(model_filename, archive_filename, extra_contents):
    params, sims, vars, outputs = get_parameters_variables_outputs_for_simulation(
        model_filename, ModelLanguage.BNGL, UniformTimeCourseSimulation, native_ids=True)

    obj_vars = list(filter(lambda var: var.target.startswith('/sbml:sbml/sbml:model/fbc:listOfObjectives/'), vars))
    rxn_flux_vars = list(filter(lambda var: var.target.startswith('/sbml:sbml/sbml:model/sbml:listOfReactions/'), vars))

    sedml_doc = SedDocument()
    model = Model(
        id='model',
        source=os.path.basename(model_filename),
        language=ModelLanguage.BNGL.value,
        changes=params,
    )
    sedml_doc.models.append(model)
    sim = sims[0]
    sedml_doc.simulations.append(sim)

    task = Task(
        id='task',
        model=model,
        simulation=sim,
    )
    sedml_doc.tasks.append(task)

    report = Report(
        id='objective',
        name='Objective',
    )
    sedml_doc.outputs.append(report)
    for var in obj_vars:
        var_id = var.id
        var_name = var.name

        var.id = 'variable_' + var_id
        var.name = None

        var.task = task
        data_gen = DataGenerator(
            id='data_generator_{}'.format(var_id),
            variables=[var],
            math=var.id,
        )
        sedml_doc.data_generators.append(data_gen)
        report.data_sets.append(DataSet(
            id=var_id,
            label=var_id,
            name=var_name,
            data_generator=data_gen,
        ))

    report = Report(
        id='reaction_fluxes',
        name='Reaction fluxes',
    )
    sedml_doc.outputs.append(report)
    for var in rxn_flux_vars:
        var_id = var.id
        var_name = var.name

        var.id = 'variable_' + var_id
        var.name = None

        var.task = task
        data_gen = DataGenerator(
            id='data_generator_{}'.format(var_id),
            variables=[var],
            math=var.id,
        )
        sedml_doc.data_generators.append(data_gen)
        report.data_sets.append(DataSet(
            id=var_id,
            label=var_id,
            name=var_name if len(rxn_flux_vars) < 4000 else None,
            data_generator=data_gen,
        ))

    # make temporary directory for archive
    archive_dirname = tempfile.mkdtemp()
    shutil.copyfile(model_filename, os.path.join(archive_dirname, os.path.basename(model_filename)))

    SedmlSimulationWriter().run(sedml_doc, os.path.join(archive_dirname, 'simulation.sedml'))

    # form a description of the archive
    archive = CombineArchive()
    archive.contents.append(CombineArchiveContent(
        location=os.path.basename(model_filename),
        format=CombineArchiveContentFormat.BNGL.value,
    ))
    archive.contents.append(CombineArchiveContent(
        location='simulation.sedml',
        format=CombineArchiveContentFormat.SED_ML.value,
    ))
    for local_path, extra_content in extra_contents.items():
        shutil.copyfile(local_path, os.path.join(archive_dirname, extra_content.location))
        archive.contents.append(extra_content)

    # save archive to file
    CombineArchiveWriter().run(archive, archive_dirname, archive_filename)

    # clean up temporary directory for archive
    shutil.rmtree(archive_dirname)
