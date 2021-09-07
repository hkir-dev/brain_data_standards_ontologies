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

    return OR_SEPARATOR.join({node[prop] for prop in synonym_properties if prop in node.keys() and node[prop]})


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
    Reads tsv file content into a dict. Key is the id column value and the value is list of row values
    Args:
        csv_path: Path of the CSV file
        id_column: Id column becomes the key of the dict. This column should be unique. Default is the first column.
        delimiter: Value delimiter. Default is comma.
        id_to_lower: applies string lowercase operation to the key

    Returns:
        CSV content dict. Key is the first column value and the value is list of row values.
    """
    records = dict()
    with open(csv_path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        for row in rd:
            _id = row[id_column]
            if id_to_lower:
                _id = str(_id).lower()
            records[_id] = row

    return records


def index_dendrogram(dend):
    dend_dict = dict()
    for o in dend['nodes']:
        dend_dict[o['cell_set_accession']] = o
    return dend_dict


def read_ensemble_data(ensemble_path):
    ensemble = {}
    with open(ensemble_path) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        # skip first 2 rows
        next(rd)
        next(rd)
        for row in rd:
            _id = row[0]
            ensemble[_id] = row[2]
    return ensemble


def read_markers(marker_path, ensmusg_names):
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
                    if marker_name in ensmusg_names:
                        names.append(marker_name)
                    else:
                        print(marker_name + " couldn't find in ensmusg.tsv")
                markers[_id] = "|".join(sorted(names))
    return markers


def get_gross_cell_type(_id, subtrees, taxonomy_config):
    gross_cell_type = ''
    for index, subtree in enumerate(subtrees):
        if _id in subtree:
            gross_cell_type = taxonomy_config['Root_nodes'][index]['Cell_type']
    return gross_cell_type
