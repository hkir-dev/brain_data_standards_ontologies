import unittest
import networkx as nx
import os
# import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from marker_tools import generate_denormalised_marker, read_dendrogram_tree, read_marker_file, \
    extend_expressions


PATH_DEND_JSON = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/CCN202002013.json")

PATH_MARKERS = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/CS202002013_markers.tsv")

PATH_OUTPUT_MARKER = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  "./test_data/CS202002013_markers_denormalised.tsv")

EXPRESSIONS = "expressions"


def delete_file(path_to_file):
    if os.path.exists(path_to_file):
        os.remove(path_to_file)


# def visualise_tree():
#     tree = read_dendrogram_tree(PATH_DEND_JSON)
#     marker_expressions = read_marker_file(PATH_MARKERS)
#
#     labels = {}
#     color_map = []
#     for node in tree.nodes():
#         labels[node] = str(node).replace("CS202002013", "")
#         # nodes that also exist in the marker file will be displayed as red, others as blue
#         if str(node) in marker_expressions.keys():
#             # light red
#             color_map.append('#F08080')
#         else:
#             # sky blue
#             color_map.append('#00BFFF')
#
#     plt.title('CCN202002013')
#     pos = graphviz_layout(tree, prog='dot')
#     nx.draw(tree, pos, node_color=color_map, with_labels=False, arrows=False)
#     nx.draw_networkx_labels(tree, pos, labels, font_size=7)
#
#     plt.show()


class DenormalisedMarkerTest(unittest.TestCase):

    def test_tree_descendants(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        descendants = nx.descendants(tree, "CS202002013_183")

        self.assertEqual(4, len(descendants))
        # direct leaf
        self.assertTrue("CS202002013_60" in descendants)
        # direct child
        self.assertTrue("CS202002013_184" in descendants)
        # child of 184
        self.assertTrue("CS202002013_58" in descendants)
        self.assertTrue("CS202002013_59" in descendants)

    def test_tree_ancestors(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        ancestors = nx.ancestors(tree, "CS202002013_213")

        print(ancestors)
        self.assertEqual(3, len(ancestors))
        self.assertTrue("CS202002013_212" in ancestors)
        self.assertTrue("CS202002013_118" in ancestors)
        self.assertTrue("CS202002013_117" in ancestors)

    def test_marker_enrichment(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        marker_expressions = read_marker_file(PATH_MARKERS)
        marker_extended_expressions = extend_expressions(tree, marker_expressions)

        # assert same IDs
        self.assertEqual(marker_expressions.keys(), marker_extended_expressions.keys())

        self.assertTrue("CS202002013_86" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_86"][EXPRESSIONS]

        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000039519" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000028031" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000045648" in expressions)
        # enriched from _207
        self.assertTrue("ensembl:ENSMUSG00000004151" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000047907" in expressions)
        # enriched from _179
        self.assertTrue("ensembl:ENSMUSG00000053025" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000032503" in expressions)

        self.assertEqual(7, len(expressions))

    def test_subtree_restrictions(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        marker_expressions = read_marker_file(PATH_MARKERS)
        # have marker
        marker_extended_expressions = extend_expressions(tree, marker_expressions, ["CS202002013_123"])

        # assert same IDs
        self.assertEqual(marker_expressions.keys(), marker_extended_expressions.keys())

        self.assertTrue("CS202002013_123" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_123"][EXPRESSIONS]
        # root should not have expressions
        self.assertEqual(0, len(expressions))

        # markers on the root node should not be inherited
        expressions = marker_extended_expressions["CS202002013_125"][EXPRESSIONS]
        # only self expressions
        self.assertTrue("ensembl:ENSMUSG00000029819" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000075270" in expressions)
        self.assertEqual(2, len(expressions))

        expressions = marker_extended_expressions["CS202002013_8"][EXPRESSIONS]
        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000110002" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000029361" in expressions)
        # inherited from 125
        self.assertTrue("ensembl:ENSMUSG00000029819" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000075270" in expressions)
        self.assertEqual(4, len(expressions))

    def test_subtree_restrictions_out_tree(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        marker_expressions = read_marker_file(PATH_MARKERS)
        # have marker
        marker_extended_expressions = extend_expressions(tree, marker_expressions, ["CS202002013_123"])

        # assert same IDs
        self.assertEqual(marker_expressions.keys(), marker_extended_expressions.keys())

        # out of subtree should not be enriched
        expressions = marker_extended_expressions["CS202002013_207"][EXPRESSIONS]
        # only self expressions
        self.assertTrue("ensembl:ENSMUSG00000004151" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000047907" in expressions)
        self.assertEqual(2, len(expressions))

    def test_subtree_restrictions2(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        marker_expressions = read_marker_file(PATH_MARKERS)
        # don't have marker
        marker_extended_expressions = extend_expressions(tree, marker_expressions, ["CS202002013_121"])

        # assert same IDs
        self.assertEqual(marker_expressions.keys(), marker_extended_expressions.keys())

        self.assertFalse("CS202002013_121" in marker_extended_expressions.keys())

        expressions = marker_extended_expressions["CS202002013_123"][EXPRESSIONS]
        # only self expressions
        self.assertTrue("ensembl:ENSMUSG00000070880" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000098326" in expressions)
        self.assertEqual(2, len(expressions))

        expressions = marker_extended_expressions["CS202002013_125"][EXPRESSIONS]
        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000029819" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000075270" in expressions)
        # inherited from 123
        self.assertTrue("ensembl:ENSMUSG00000070880" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000098326" in expressions)
        self.assertEqual(4, len(expressions))

        expressions = marker_extended_expressions["CS202002013_8"][EXPRESSIONS]
        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000110002" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000029361" in expressions)
        # inherited from 125
        self.assertTrue("ensembl:ENSMUSG00000029819" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000075270" in expressions)
        # inherited from 123
        self.assertTrue("ensembl:ENSMUSG00000070880" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000098326" in expressions)
        self.assertEqual(6, len(expressions))

    def test_subtree_restrictions3(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        marker_expressions = read_marker_file(PATH_MARKERS)
        marker_extended_expressions = extend_expressions(tree, marker_expressions,
                                                         ["CS202002013_132", "CS202002013_179"])

        # assert same IDs
        self.assertEqual(marker_expressions.keys(), marker_extended_expressions.keys())

        self.assertTrue("CS202002013_179" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_179"][EXPRESSIONS]
        self.assertEqual(0, len(expressions))

        # 207 is child of 179
        self.assertTrue("CS202002013_207" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_207"][EXPRESSIONS]
        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000004151" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000047907" in expressions)
        self.assertEqual(2, len(expressions))

        # 88 is child of 207
        self.assertTrue("CS202002013_88" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_88"][EXPRESSIONS]
        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000026344" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000047907" in expressions)
        # enriched from _207
        self.assertTrue("ensembl:ENSMUSG00000004151" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000047907" in expressions)
        # one duplicate
        self.assertEqual(3, len(expressions))

        # 86 is child of 207
        self.assertTrue("CS202002013_86" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_86"][EXPRESSIONS]
        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000039519" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000028031" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000045648" in expressions)
        # enriched from _207
        self.assertTrue("ensembl:ENSMUSG00000004151" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000047907" in expressions)
        self.assertEqual(5, len(expressions))

        self.assertFalse("CS202002013_132" in marker_extended_expressions.keys())

        # 133 is child of 132
        self.assertTrue("CS202002013_133" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_133"][EXPRESSIONS]
        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000044288" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000058897" in expressions)
        print(expressions)
        self.assertEqual(2, len(expressions))

        # 9 is child of 133
        self.assertTrue("CS202002013_9" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_9"][EXPRESSIONS]
        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000039385" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000058897" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000015766" in expressions)
        # enriched from _132
        self.assertTrue("ensembl:ENSMUSG00000044288" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000058897" in expressions)
        # one duplicate
        self.assertEqual(4, len(expressions))

        # 11 is child of 132
        self.assertTrue("CS202002013_11" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_11"][EXPRESSIONS]
        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000063661" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000042045" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000027849" in expressions)
        # enriched from _132
        self.assertTrue("ensembl:ENSMUSG00000044288" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000058897" in expressions)
        self.assertEqual(5, len(expressions))

    # def test_marker_generation(self):
    #     delete_file(PATH_OUTPUT_MARKER)
    #
    #     generate_denormalised_marker(PATH_DEND_JSON, PATH_MARKERS, PATH_OUTPUT_MARKER)
    #     self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()