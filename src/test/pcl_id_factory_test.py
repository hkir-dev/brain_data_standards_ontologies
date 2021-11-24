import unittest
from pcl_id_factory import get_class_id, get_individual_id, taxonomy_ids, get_taxonomy_id, get_reverse_id
from template_generation_utils import migrate_manual_curations


class PCLIdFactoryTestCase(unittest.TestCase):

    def test_taxonomy_ids_parsing(self):
        self.assertTrue(len(taxonomy_ids) >= 4)
        self.assertEqual("CCN202002013", taxonomy_ids[0])
        self.assertEqual("CCN201912131", taxonomy_ids[1])
        self.assertEqual("CCN201912132", taxonomy_ids[2])
        self.assertEqual("CS1908210", taxonomy_ids[3])

    def test_mouse_ids(self):
        self.assertEqual(get_class_id("CS202002013_1"), "0011001")
        self.assertEqual(get_class_id("CS202002013_121"), "0011121")

        self.assertEqual(get_individual_id("CS202002013_1"), "0011401")
        self.assertEqual(get_individual_id("CS202002013_121"), "0011521")

    def test_human_ids(self):
        self.assertEqual(get_class_id("CS201912131_1"), "0012001")
        self.assertEqual(get_class_id("CS201912131_121"), "0012121")

        self.assertEqual(get_individual_id("CS201912131_1"), "0012401")
        self.assertEqual(get_individual_id("CS201912131_121"), "0012521")

    def test_marmoset_ids(self):
        self.assertEqual(get_class_id("CS201912132_1"), "0013001")
        self.assertEqual(get_class_id("CS201912132_121"), "0013121")

        self.assertEqual(get_individual_id("CS201912132_1"), "0013401")
        self.assertEqual(get_individual_id("CS201912132_121"), "0013521")

    def test_human_mtg_ids(self):
        self.assertEqual(get_class_id("CS1908210001"), "0014001")
        self.assertEqual(get_class_id("CS1908210148"), "0014148")

        self.assertEqual(get_individual_id("CS1908210001"), "0014401")
        self.assertEqual(get_individual_id("CS1908210148"), "0014548")

    def test_taxonomy_id(self):
        self.assertEqual(get_taxonomy_id("CS202002013"), "0011000")
        self.assertEqual(get_taxonomy_id("CCN202002013"), "0011000")

        self.assertEqual(get_taxonomy_id("CS201912131"), "0012000")
        self.assertEqual(get_taxonomy_id("CCN201912131"), "0012000")

        self.assertEqual(get_taxonomy_id("CS201912132"), "0013000")
        self.assertEqual(get_taxonomy_id("CCN201912132"), "0013000")

        self.assertEqual(get_taxonomy_id("CS1908210"), "0014000")

    def test_reverse_id(self):
        self.assertEqual(get_reverse_id("0011001"), "CS202002013_1")
        self.assertEqual(get_reverse_id("PCL_0011001"), "CS202002013_1")
        self.assertEqual(get_reverse_id("PCL:0011001"), "CS202002013_1")
        self.assertEqual(get_reverse_id("http://purl.obolibrary.org/obo/PCL_0011001"), "CS202002013_1")

        self.assertEqual(get_reverse_id("0011521"), "CS202002013_121")
        self.assertEqual(get_reverse_id("0012121"), "CS201912131_121")
        self.assertEqual(get_reverse_id("0013401"), "CS201912132_1")
        self.assertEqual(get_reverse_id("0014548"), "CS1908210148")
        self.assertEqual(get_reverse_id("0014001"), "CS1908210001")

    # not test
    # def test_allen_markers_migrate(self):
    #     migrate_columns = ["Obsoleted By"]
    #     migrate_manual_curations("../templates/pCL_mapping_old.tsv",
    #                              "../templates/pCL_mapping.tsv",
    #                              migrate_columns,
    #                              "../templates/pCL_mapping_merged.tsv")


if __name__ == '__main__':
    unittest.main()
