"""
Pruebas de la Fase 1 de BioSim Lab:
ADN, copia, mutaciones y mecanismos simplificados de reparacion.
Criterios de aceptacion definidos en la Seccion 5 de la Guia de Programacion.
"""

import unittest
from app.services.dna_engine import DNAEngine

class TestDNAPhase1(unittest.TestCase):
    def setUp(self):
        self.engine = DNAEngine()

    def test_01_secuencia_valida(self):
        """Prueba 1: ATCG debe ser aceptada."""
        self.assertTrue(self.engine.validate("ATCG"))
        self.assertTrue(self.engine.validate("atcg"))
        self.assertTrue(self.engine.validate("GATTACA"))

    def test_02_simbolo_no_valido(self):
        """Prueba 2: ATXG debe ser rechazada y generar error controlado en operaciones."""
        self.assertFalse(self.engine.validate("ATXG"))
        self.assertFalse(self.engine.validate("1234"))
        self.assertFalse(self.engine.validate("ATC G")) # espacio
        with self.assertRaises(ValueError):
            self.engine.complement("ATXG")
        with self.assertRaises(ValueError):
            self.engine.copy_dna("ATXG")

    def test_03_complementariedad(self):
        """Prueba 3: Para ATCG, complementaria simplificada esperada es TAGC."""
        comp = self.engine.complement("ATCG")
        self.assertEqual(comp, "TAGC")

    def test_04_copia_secuencia(self):
        """Prueba 4: Copia de GATTACA debe coincidir exactamente con la entrada."""
        res = self.engine.copy_dna("GATTACA")
        self.assertEqual(res["original"], "GATTACA")
        self.assertEqual(res["copy"], "GATTACA")
        self.assertTrue(res["is_identical"])
        self.assertEqual(res["length"], 7)

    def test_05_mutacion_controlada(self):
        """Prueba 5: ATCG -> cambiar base de forma controlada en una posicion."""
        # Cambiar indice 1 ('T') por 'A' -> 'AACG'
        res = self.engine.apply_controlled_mutation("ATCG", "substitution", 1, "A")
        self.assertEqual(res["modified_sequence"], "AACG")
        self.assertEqual(res["original_sequence"], "ATCG")
        self.assertEqual(res["mutation"]["position"], 1)

    def test_06_apareamiento_incorrecto(self):
        """Prueba 6: Cadena 1: A; Cadena 2: G -> Marca pareja no canonica (mismatch)."""
        res = self.engine.detect_mismatches("A", "G")
        self.assertFalse(res["is_fully_canonical"])
        self.assertEqual(res["mismatch_count"], 1)
        self.assertEqual(res["canonical_count"], 0)
        self.assertEqual(res["mismatches"][0]["status"], "mismatch")
        self.assertIn("Apareamiento no canonico", res["mismatches"][0]["note"])

    def test_07_reparacion_con_referencia(self):
        """
        Prueba 7: Referencia ATCG; version alterada con base distinta (ej. ACCG).
        Tras reparar la posicion indicada (pos 1), debe coincidir con la referencia.
        """
        alt = "ACCG"
        ref = "ATCG"
        res = self.engine.repair_with_reference(altered=alt, reference=ref, positions=[1])
        self.assertEqual(res["repaired_sequence"], "ATCG")
        self.assertTrue(res["matches_reference"])
        self.assertEqual(res["repaired_positions"], [1])
        self.assertEqual(res["status"], "fully_repaired")

    def test_08_sin_referencia_fiable(self):
        """
        Prueba 8: Sin referencia fiable, el sistema no conjetura la base original,
        unicamente detecta la discrepancia.
        Cadena 1: ATCG (su par canonico es TAGC).
        Cadena 2: TTGC (en pos 1 tiene T en vez de A, formando par T-T).
        """
        res = self.engine.detect_mismatches("ATCG", "TTGC")
        self.assertFalse(res["is_fully_canonical"])
        mismatch_items = res["mismatches"]
        self.assertEqual(len(mismatch_items), 1)
        self.assertEqual(mismatch_items[0]["position"], 1)
        self.assertEqual(mismatch_items[0]["pair"], "T-T")
        self.assertIn("no se puede inferir", mismatch_items[0]["note"])

    def test_09_rotura_y_reparacion_extension(self):
        """Prueba 9: Rotura de ADN (DSB) con HDR (asistido por referencia) y NHEJ."""
        seq = "GATTACAGATTACA"
        break_pos = 6
        # HDR con referencia
        hdr_res = self.engine.simulate_break_repair(seq, break_pos, method="homology_directed", reference=seq)
        self.assertEqual(hdr_res["repaired_sequence"], seq)
        self.assertTrue(hdr_res["matches_initial"])
        
        # NHEJ sin referencia
        nhej_res = self.engine.simulate_break_repair(seq, break_pos, method="end_joining")
        self.assertIn(nhej_res["status"], ["repaired_prone_to_scar", "repaired_high_fidelity"])

    def test_10_registro_eventos(self):
        """Prueba 10: Trazabilidad y registro de eventos con identificador y suposiciones del modelo."""
        events = self.engine.get_events(limit=5)
        self.assertGreater(len(events), 0)
        latest = events[0]
        self.assertTrue(latest["experiment_id"].startswith("EXP-"))
        self.assertIn("model_assumptions", latest)
        self.assertEqual(latest["code_version"], "v1.1-phase1-closed")

    def test_11_guardar_y_cargar_experimento_completo(self):
        """Prueba 11: Construccion del informe completo (la persistencia se hace en la BD, no en JSON)."""
        exp_data = {
            "name": "Ensayo de Replicación y Reparación MMR",
            "initial_sequence": "ATCGATCGATCG",
            "working_copy": "ATCGATCGATCG",
            "mutation_applied": {"type": "substitution", "position": 4, "new_base": "G"},
            "altered_sequence": "ATCGGTCGATCG",
            "detection_result": {"mismatch_count": 1, "mismatches": [{"position": 4, "pair": "G-T"}]},
            "repair_applied": {"status": "repaired_full_match", "repaired_sequence": "ATCGATCGATCG"},
            "final_sequence": "ATCGATCGATCG",
            "status": "repaired_full_match"
        }
        saved = self.engine.build_experiment_record(exp_data)
        self.assertTrue(saved["experiment_id"].startswith("EXP-"))
        self.assertEqual(saved["name"], "Ensayo de Replicación y Reparación MMR")
        self.assertEqual(saved["initial_sequence"], "ATCGATCGATCG")
        self.assertEqual(saved["final_sequence"], "ATCGATCGATCG")
        self.assertEqual(saved["mutation_applied"]["new_base"], "G")

    def test_12_triple_filtro_fase_s_y_checkpoint_g1(self):
        """
        Prueba 12: Verificacion del triple filtro de fidelidad en fase S
        (Polimerasa 10^5, Exonucleasa 10^7, MMR 10^9-10^10) y del punto de control G1/S con p53/p21.
        """
        # Prueba Fase S: Triple filtro
        rep_res = self.engine.replicate_with_mutations("ATCGATCG", mutation_rate=0.0)
        self.assertIn("fidelity_filters", rep_res)
        filters = rep_res["fidelity_filters"]
        self.assertIn("filter_1_polymerase", filters)
        self.assertIn("filter_2_proofreading", filters)
        self.assertIn("filter_3_mismatch_repair", filters)
        self.assertEqual(filters["filter_1_polymerase"]["error_rate"], "1 en 10^5")
        self.assertEqual(filters["filter_2_proofreading"]["error_rate"], "1 en 10^7")
        self.assertEqual(filters["filter_3_mismatch_repair"]["error_rate"], "1 en 10^9 - 10^10")

        # Prueba Fase G1: Checkpoint G1/S p53/p21
        repair_res = self.engine.repair_with_reference(altered="ATGG", reference="ATCG")
        self.assertEqual(repair_res["cell_cycle_phase"], "G1")
        self.assertIn("checkpoint_status", repair_res)
        cp = repair_res["checkpoint_status"]
        self.assertEqual(cp["phase"], "G1")
        self.assertIn("p53", cp["sensor"])
        self.assertIn("p21", cp["sensor"])
        self.assertIn("Autorizado a Fase S", cp["outcome"])

if __name__ == "__main__":
    unittest.main()
