import yaml
import os
import csv
import networkx as nx
import json

from dendrogram_tools import tree_recurse


TAXONOMY_DETAILS_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     '../dendrograms/taxonomy_details.yaml')

EXPRESSIONS = "expressions"
OR_SEPARATOR = '|'
PAIR_SEPARATOR = ' ; '


def get_synonyms_from_taxonomy(node):
    """
    Returns synonyms string generated by concatenating the content of the following fields with each value separated
    by |: cell_set_preferred_alias, original_label, cell_set_label, cell_set_aligned_alias, cell_set_additional_alias
    Args:
        node: Dendrogram node to get synonyms

    Returns: name synonyms string concatenated by "|"

    """
    synonym_properties = ['cell_set_preferred_alias', 'original_label', 'cell_set_label', 'cell_set_aligned_alias',
                          'cell_set_additional_aliases']
    synonyms = {node[prop] for prop in synonym_properties if prop in node.keys() and node[prop]}

    return OR_SEPARATOR.join(sorted(synonyms))


def get_synonym_pairs(node):
    """
    Returns the synonym key-value paris in the form {key} : {value} sep=" ; ".
    Fields: cell_set_preferred_alias, original_label, cell_set_label, cell_set_aligned_alias, cell_set_additional_alias
    Args:
        node:

    Returns:

    """
    synonym_properties = ['cell_set_preferred_alias', 'original_label', 'cell_set_label', 'cell_set_aligned_alias',
                          'cell_set_additional_aliases']
    values = []
    for prop in synonym_properties:
        if prop in node.keys():
            pair_str = prop + ":"
            pair_str += node[prop] if node[prop] else "''"
            values.append(pair_str)
    return PAIR_SEPARATOR.join(values)


def read_taxonomy_config(taxon):
    config = read_taxonomy_details_yaml()
    taxonomy_config = get_taxonomy_configuration(config, taxon)
    return taxonomy_config


def read_taxonomy_details_yaml():
    with open(r'%s' % TAXONOMY_DETAILS_YAML) as file:
        documents = yaml.full_load(file)
    return documents


def get_taxonomy_configuration(config, taxonomy):
    """
    Lists all taxonomies that has a configuration in the config
    Args:
        config: configuration file
        taxonomy: taxonomy to get its configuration

    Returns: List of taxonomy names that has a configuration

    """
    for taxonomy_config in config:
        if taxonomy_config["Taxonomy_id"] == taxonomy:
            return taxonomy_config
    return


def get_max_marker_count(marker_expressions):
    """
    Returns the maximum number of markers in the given marker definition
    Args:
        marker_expressions: marker file content

    Returns: the maximum number of markers in the given marker definition

    """
    max_count = 0
    for term in marker_expressions.keys():
        expression_count = len(marker_expressions.get(term)[EXPRESSIONS])
        if expression_count > max_count:
            max_count = expression_count

    return max_count


def read_dendrogram_tree(dend_json_path):
    """
    Reads the dendrogram file and builds a tree representation using the edges.
    Args:
        dend_json_path: Path of the dendrogram file

    Returns: networkx directed graph that represents the taxonomy

    """
    with open(dend_json_path, 'r') as f:
        j = json.loads(f.read())

    out = {}
    tree_recurse(j, out)

    tree = nx.DiGraph()
    for edge in out['edges']:
        tree.add_edge(edge[1], edge[0])

    return tree


def generate_dendrogram_tree(dendrogram_data):
    """
    Generates a tree representation using the edges of the dendrogram data.
    Args:
        dendrogram_data: Parsed dendrogram file data

    Returns: networkx directed graph that represents the taxonomy

    """
    tree = nx.DiGraph()
    for edge in dendrogram_data['edges']:
        tree.add_edge(edge[1], edge[0])

    return tree


def get_dend_subtrees(dend_json_path):
    """
    Reads both the dendrogram and the elated config file and returns subtrees defined in the config file through
    utilizing Root_nodes.
    Args:
        dend_json_path: path to the dendrogram file.

    Returns: list of subtree nodes list

    """
    dend_tree = read_dendrogram_tree(dend_json_path)

    path_parts = dend_json_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]
    config_yaml = read_taxonomy_config(taxon)

    subtrees = get_subtrees(dend_tree, config_yaml)
    return subtrees


def get_subtrees(dend_tree, taxonomy_config):
    """
    For each root node in the taxonomy creates the list of subtree nodes
    Args:
        dend_tree: dendrogram networkx representation
        taxonomy_config: taxonomy configuration

    Returns: list of subtree nodes

    """
    subtrees = []
    for root_node in taxonomy_config['Root_nodes']:
        descendants = nx.descendants(dend_tree, root_node['Node'])
        # subtrees exclude root node itself, if not root and leaf at the same time
        if len(descendants) == 0:
            descendants.add(root_node['Node'])
        subtrees.append(descendants)
    return subtrees


def get_root_nodes(config_yaml):
    """
    List the root nodes defined in the given taxonomy config.
    Args:
        config_yaml: configuration content

    Returns: list of root nodes

    """
    root_nodes = []
    for root_node in config_yaml['Root_nodes']:
        root_nodes.append(root_node['Node'])
    return root_nodes


def read_tsv(tsv_path, id_column=0):
    """
    @DEPRECATED: Please use read_tsv_to_dict. Dictionary based approach deals better with changing column orders and
    missing columns that occur in nomenclature tables.

    Reads tsv file content into a dict. Key is the first column value and the value is list of row values
    Args:
        tsv_path: Path of the TSV file
        id_column: Id column becomes the key of the dict. This column should be unique. Default is the first column.
    Returns:
        TSV content dict. Key is the first column value and the value is list of row values.
    """
    return read_csv(tsv_path, id_column=id_column, delimiter="\t")


def read_csv(csv_path, id_column=0, delimiter=",", id_to_lower=False):
    """
    @DEPRECATED: Please use read_csv_to_dict. Dictionary based approach deals better with changing column orders and
    missing columns that occur in nomenclature tables.

    Reads tsv file content into a dict. Key is the id column value and the value is list of row values
    Args:
        csv_path: Path of the CSV file
        id_column: Id column becomes the keys of the dict. This column should be unique. Default is the first column.
        delimiter: Value delimiter. Default is comma.
        id_to_lower: applies string lowercase operation to the key

    Returns:
        CSV content dict. Key is the first column value and the value is list of row values.
    """
    records = dict()
    with open(csv_path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        # skip first row
        next(rd)
        for row in rd:
            _id = row[id_column]
            if id_to_lower:
                _id = str(_id).lower()
            records[_id] = row

    return records


def read_tsv_to_dict(tsv_path, id_column=0):
    """
    Reads tsv file content into a dict. Key is the first column value and the value is dict representation of the
    row values (each header is a key and column value is the value).
    Args:
        tsv_path: Path of the TSV file
        id_column: Id column becomes the key of the dict. This column should be unique. Default value is first column.
    Returns:
        Function provides two return values: first; headers of the table and second; the TSV content dict. Key of the
        content is the first column value and the values are dict of row values.
    """
    return read_csv_to_dict(tsv_path, id_column=id_column, delimiter="\t")


def read_csv_to_dict(csv_path, id_column=0, id_column_name="", delimiter=",", id_to_lower=False):
    """
    Reads tsv file content into a dict. Key is the first column value and the value is dict representation of the
    row values (each header is a key and column value is the value).
    Args:
        csv_path: Path of the CSV file
        id_column: Id column becomes the keys of the dict. This column should be unique. Default is the first column.
        id_column_name: Alternative to the numeric id_column, id_column_name specifies id_column by its header string.
        delimiter: Value delimiter. Default is comma.
        id_to_lower: applies string lowercase operation to the key

    Returns:
        Function provides two return values: first; headers of the table and second; the CSV content dict. Key of the
        content is the first column value and the values are dict of row values.
    """
    records = dict()

    headers = []
    with open(csv_path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        row_count = 0
        for row in rd:
            _id = row[id_column]
            if id_to_lower:
                _id = str(_id).lower()

            if row_count == 0:
                headers = row
                if id_column_name:
                    id_column = headers.index(id_column_name)
            else:
                row_object = dict()
                for column_num, column_value in enumerate(row):
                    row_object[headers[column_num]] = column_value
                records[_id] = row_object

            row_count += 1

    return headers, records


def index_dendrogram(dend):
    dend_dict = dict()
    for o in dend['nodes']:
        dend_dict[o['cell_set_accession']] = o
    return dend_dict


def read_gene_data(gene_db_path):
    genes = {}
    with open(gene_db_path) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        # skip first 2 header rows
        next(rd)
        next(rd)
        for row in rd:
            _id = row[0]
            genes[_id] = row[2]
    return genes


def read_markers(marker_path, gene_names):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), marker_path)
    markers = {}

    with open(path) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        # skip first row
        next(rd)
        for row in rd:
            _id = row[0]

            names = []
            if row[2]:
                for marker in row[2].split("|"):
                    marker_name = marker.strip()
                    if marker_name in gene_names:
                        names.append(marker_name)
                    else:
                        print(marker_name + " couldn't find in gene names database.")
                markers[_id] = "|".join(sorted(names))
    return markers


def get_gross_cell_type(_id, subtrees, taxonomy_config):
    gross_cell_type = ''
    for index, subtree in enumerate(subtrees):
        if _id in subtree:
            gross_cell_type = taxonomy_config['Root_nodes'][index]['Cell_type']
    return gross_cell_type


def merge_tables(base_tsv, extension_tsv, output_filepath):
    """
    Applies all columns of the extension_tsv to the base tsv and generates a new table in the output_filepath.
    Args:
        base_tsv: Base table to add new columns.
        extension_tsv: Extension table
        output_filepath: Output file path
    """
    base_headers, base = read_tsv_to_dict(base_tsv)
    extension_headers, extension = read_tsv_to_dict(extension_tsv)

    migrate_columns = [x for x in extension_headers if x not in base_headers]
    merged_headers = base_headers + (list(migrate_columns))

    with open(output_filepath, mode='w') as out:
        writer = csv.writer(out, delimiter="\t", quotechar='"')
        writer.writerow(merged_headers)

        for key, row_data in base.items():
            if key in extension:
                for migrate_column in migrate_columns:
                    if migrate_column in extension[key]:
                        row_data[migrate_column] = extension[key][migrate_column]
                    else:
                        row_data[migrate_column] = ''
            else:
                for migrate_column in migrate_columns:
                    row_data[migrate_column] = ''

            row = list()
            for column in merged_headers:
                row.append(row_data[column])

            writer.writerow(row)


def migrate_manual_curations(source_tsv, target_tsv, migrate_columns, output_filepath):
    """
    Copies manual curations (for the specified columns) from source file to the target file and generates a
    new migration file.
    Args:
        source_tsv: Source table to read manual curations from.
        target_tsv: Target table to append manual curations to.
        migrate_columns: list of the columns to copy their values from source to target.
        output_filepath: Output file path
    """
    base_headers, base = read_tsv_to_dict(source_tsv)
    target_headers, target = read_tsv_to_dict(target_tsv)

    # migrate_columns = [x for x in extension_headers if x not in base_headers]
    # merged_headers = base_headers + (list(migrate_columns))

    with open(output_filepath, mode='w') as out:
        writer = csv.writer(out, delimiter="\t", quotechar='"')
        writer.writerow(target_headers)

        for key, row_data in target.items():
            if key in base:
                for migrate_column in migrate_columns:
                    if migrate_column in base[key]:
                        row_data[migrate_column] = base[key][migrate_column]
                    else:
                        row_data[migrate_column] = ''
            else:
                for migrate_column in migrate_columns:
                    row_data[migrate_column] = ''

            row = list()
            for column in target_headers:
                row.append(row_data[column])

            writer.writerow(row)


def read_allen_descriptions(path, species):
    """
    Reads Allen descriptions file from the given location for the given species.
    Args:
        path: Path to the All Descriptions json file
        species: species to read file for
    Returns: parsed Allen descriptions json data
    """
    allen_descriptions_path = path.format(species)
    if os.path.isfile(allen_descriptions_path):
        with open(allen_descriptions_path, 'r') as f:
            allen_descriptions = json.loads(f.read())
    else:
        allen_descriptions = {}
    return allen_descriptions
