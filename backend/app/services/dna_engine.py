import random
from typing import List, Dict, Any, Optional

class DNAEngine:
    """
    Motor bio-computacional para la Fase 1 de BioSIM Lab.
    Implementa reglas abstractas sobre secuencias artificiales de nucleotidos:
    validacion, complementariedad, codificacion binaria, mutaciones controladas,
    replicacion semiconservativa con tasa de error y deteccion de diferencias (diff).
    """

    VALID_BASES = {"A", "T", "C", "G"}
    COMPLEMENT_MAP = {"A": "T", "T": "A", "C": "G", "G": "C"}
    BINARY_MAP = {"A": "00", "T": "11", "C": "01", "G": "10"}
    INV_BINARY_MAP = {"00": "A", "11": "T", "01": "C", "10": "G"}

    @classmethod
    def validate(cls, sequence: str) -> bool:
        """Comprueba que una secuencia solo contenga A, T, C y G (insensible a mayusculas)."""
        if not sequence:
            return False
        clean = sequence.upper().strip()
        return all(base in cls.VALID_BASES for base in clean)

    @classmethod
    def complement(cls, sequence: str) -> str:
        """Genera la cadena complementaria A<->T y C<->G."""
        clean = sequence.upper().strip()
        if not cls.validate(clean):
            raise ValueError("Secuencia invalida: contiene caracteres distintos a A, T, C, G")
        return "".join(cls.COMPLEMENT_MAP[base] for base in clean)

    @classmethod
    def to_binary(cls, sequence: str) -> str:
        """Codificacion binaria de 2 bits segun seccion 6.2 del doc: A=00, T=11, C=01, G=10."""
        clean = sequence.upper().strip()
        if not cls.validate(clean):
            raise ValueError("Secuencia invalida para codificacion binaria")
        return "".join(cls.BINARY_MAP[base] for base in clean)

    @classmethod
    def from_binary(cls, binary_str: str) -> str:
        """Decodifica una cadena de pares de bits a secuencia de ADN."""
        clean = binary_str.strip()
        if len(clean) % 2 != 0:
            raise ValueError("Cadena binaria debe tener longitud par")
        bases = []
        for i in range(0, len(clean), 2):
            pair = clean[i:i+2]
            if pair not in cls.INV_BINARY_MAP:
                raise ValueError(f"Par binario invalido: {pair}")
            bases.append(cls.INV_BINARY_MAP[pair])
        return "".join(bases)

    @classmethod
    def apply_controlled_mutation(
        cls,
        sequence: str,
        mutation_type: str,
        position: int,
        new_base: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modo 2: Aplica una mutacion controlada como evento de prueba.
        mutation_type: 'substitution', 'insertion', 'deletion'
        """
        clean = sequence.upper().strip()
        if not cls.validate(clean):
            raise ValueError("Secuencia original invalida")

        length = len(clean)
        m_type = mutation_type.lower()

        if m_type in ("substitution", "deletion") and (position < 0 or position >= length):
            raise ValueError(f"Posicion {position} fuera de rango para {m_type} (longitud: {length})")
        elif m_type == "insertion" and (position < 0 or position > length):
            raise ValueError(f"Posicion {position} fuera de rango para insercion (longitud: {length})")

        seq_list = list(clean)
        original_base = clean[position] if position < length else None
        target_base = new_base.upper() if new_base else None

        if m_type == "substitution":
            if not target_base or target_base not in cls.VALID_BASES:
                raise ValueError("Base invalida para sustitucion. Debe ser A, T, C o G.")
            seq_list[position] = target_base

        elif m_type == "insertion":
            if not target_base or target_base not in cls.VALID_BASES:
                raise ValueError("Base invalida para insercion. Debe ser A, T, C o G.")
            seq_list.insert(position, target_base)

        elif m_type == "deletion":
            seq_list.pop(position)
            target_base = None

        else:
            raise ValueError(f"Tipo de mutacion no soportado: {mutation_type}")

        modified_seq = "".join(seq_list)
        event = cls.log_event(
            operation_type="controlled_mutation",
            initial_sequence=clean,
            final_sequence=modified_seq,
            parameters={
                "mutation_type": m_type,
                "position": position,
                "original_base": original_base if m_type != "insertion" else None,
                "new_base": target_base
            },
            reference_used=clean,
            detection_result={"status": "mutation_introduced"},
            repair_result={"status": "altered"}
        )
        return {
            "original_sequence": clean,
            "modified_sequence": modified_seq,
            "mutation": {
                "type": m_type,
                "position": position,
                "original_base": original_base if m_type != "insertion" else None,
                "new_base": target_base,
                "mode": "controlled"
            },
            "event_id": event["experiment_id"]
        }

    @classmethod
    def replicate_with_mutations(
        cls,
        sequence: str,
        mutation_rate: float = 0.0,
        substitution_weight: float = 0.70,
        insertion_weight: float = 0.15,
        deletion_weight: float = 0.15
    ) -> Dict[str, Any]:
        """
        Modo 1: Simula la replicacion con una tasa de error probabilistica (estocastica).
        Devuelve la secuencia duplicada y la lista de mutaciones ocurridas.
        """
        clean = sequence.upper().strip()
        if not cls.validate(clean):
            raise ValueError("Secuencia original invalida")

        mutated_bases = []
        mutations_log: List[Dict[str, Any]] = []
        all_bases = list(cls.VALID_BASES)

        for i, base in enumerate(clean):
            if mutation_rate > 0 and random.random() < mutation_rate:
                event_type = random.choices(
                    ["substitution", "insertion", "deletion"],
                    weights=[substitution_weight, insertion_weight, deletion_weight]
                )[0]

                if event_type == "substitution":
                    other_bases = [b for b in all_bases if b != base]
                    sub_base = random.choice(other_bases)
                    mutated_bases.append(sub_base)
                    mutations_log.append({
                        "type": "substitution",
                        "position": i,
                        "original_base": base,
                        "new_base": sub_base,
                        "mode": "stochastic"
                    })
                elif event_type == "insertion":
                    ins_base = random.choice(all_bases)
                    mutated_bases.extend([base, ins_base])
                    mutations_log.append({
                        "type": "insertion",
                        "position": i,
                        "original_base": None,
                        "new_base": ins_base,
                        "mode": "stochastic"
                    })
                elif event_type == "deletion":
                    mutations_log.append({
                        "type": "deletion",
                        "position": i,
                        "original_base": base,
                        "new_base": None,
                        "mode": "stochastic"
                    })
            else:
                mutated_bases.append(base)

        replicated_seq = "".join(mutated_bases)
        return {
            "original_sequence": clean,
            "replicated_sequence": replicated_seq,
            "mutations": mutations_log,
            "mutation_count": len(mutations_log),
            "is_identical": clean == replicated_seq
        }

    @classmethod
    def compare(cls, reference: str, modified: str) -> List[Dict[str, Any]]:
        """
        Detecta diferencias entre la secuencia de referencia y la modificada.
        Genera reporte de cambios para visualizacion de Diff en la UI.
        """
        ref = reference.upper().strip()
        mod = modified.upper().strip()
        diffs = []
        max_len = max(len(ref), len(mod))

        for i in range(max_len):
            b_ref = ref[i] if i < len(ref) else None
            b_mod = mod[i] if i < len(mod) else None

            if b_ref != b_mod:
                diffs.append({
                    "position": i,
                    "reference_base": b_ref,
                    "modified_base": b_mod,
                    "status": "changed" if b_ref and b_mod else ("deleted" if b_ref else "inserted")
                })

        return diffs

    _events_log: List[Dict[str, Any]] = []

    @classmethod
    def copy_dna(cls, sequence: str) -> Dict[str, Any]:
        """
        Genera una copia sin cambios y comprueba que coincida exactamente con la original.
        """
        clean = sequence.upper().strip()
        if not cls.validate(clean):
            raise ValueError("Secuencia invalida para copia: contiene caracteres no canonicos")
        copy_seq = str(clean)
        is_identical = (copy_seq == clean)

        event = cls.log_event(
            operation_type="copy",
            initial_sequence=clean,
            final_sequence=copy_seq,
            parameters={"length": len(clean)},
            reference_used=clean,
            detection_result={"is_identical": is_identical},
            repair_result={"status": "copied_exact", "differences": 0}
        )
        return {
            "original": clean,
            "copy": copy_seq,
            "is_identical": is_identical,
            "length": len(clean),
            "event_id": event["experiment_id"]
        }

    @classmethod
    def detect_mismatches(cls, strand1: str, strand2: str) -> Dict[str, Any]:
        """
        3.1. Deteccion de apareamientos incorrectos (Mismatch Detection).
        Comprueba si cada pareja cumple las reglas canonicas A-T (o T-A) y C-G (o G-C).
        Marca como error parejas no canonicas (ej: A-G, C-T, etc.).
        Nota: sin plantilla o referencia fiable, el sistema marca el error pero NO afirma
        que conoce automaticamente la base original correcta.
        """
        s1 = strand1.upper().strip()
        s2 = strand2.upper().strip()
        if not cls.validate(s1) or not cls.validate(s2):
            raise ValueError("Ambas cadenas deben ser secuencias validas de A, T, C, G")

        max_len = max(len(s1), len(s2))
        mismatches = []
        canonical_count = 0

        for i in range(max_len):
            b1 = s1[i] if i < len(s1) else None
            b2 = s2[i] if i < len(s2) else None

            # Regla canonica Watson-Crick
            is_canonical = False
            pair_label = f"{b1 or '∅'}-{b2 or '∅'}"
            if b1 and b2:
                is_canonical = (cls.COMPLEMENT_MAP.get(b1) == b2)

            if is_canonical:
                canonical_count += 1
            else:
                mismatches.append({
                    "position": i,
                    "base_strand1": b1,
                    "base_strand2": b2,
                    "pair": pair_label,
                    "is_canonical": False,
                    "status": "mismatch" if (b1 and b2) else ("unpaired_gap" if b1 else "extra_base"),
                    "note": "Apareamiento no canonico detectado; no se puede inferir base original sin referencia fiable."
                })

        is_fully_canonical = (len(mismatches) == 0 and len(s1) == len(s2))
        event = cls.log_event(
            operation_type="mismatch_detection",
            initial_sequence=s1,
            final_sequence=s2,
            parameters={"strand1_length": len(s1), "strand2_length": len(s2)},
            reference_used=None,
            detection_result={
                "mismatch_count": len(mismatches),
                "is_fully_canonical": is_fully_canonical,
                "canonical_pairs": canonical_count
            },
            repair_result={"status": "detected_only", "corrected": False}
        )
        return {
            "strand1": s1,
            "strand2": s2,
            "length": max_len,
            "is_fully_canonical": is_fully_canonical,
            "mismatch_count": len(mismatches),
            "canonical_count": canonical_count,
            "mismatches": mismatches,
            "event_id": event["experiment_id"]
        }

    @classmethod
    def repair_with_reference(
        cls,
        altered: str,
        reference: str,
        positions: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        3.2. Reparacion guiada por una referencia (Template-guided repair).
        Compara la secuencia alterada con una referencia fiable y reemplaza
        unicamente las posiciones autorizadas/seleccionadas por la regla.
        Registra que posiciones se cambiaron y si la secuencia final coincide con la referencia.
        Distingue explicitamente entre correccion respaldada por referencia y conjetura.
        """
        alt = altered.upper().strip()
        ref = reference.upper().strip()
        if not cls.validate(alt) or not cls.validate(ref):
            raise ValueError("Secuencias alterada y de referencia deben ser secuencias validas de A, T, C, G")

        diffs = cls.compare(ref, alt)
        diff_positions = {d["position"] for d in diffs}

        target_positions = set(positions) if positions is not None else diff_positions

        alt_list = list(alt)
        repaired_positions = []

        for pos in sorted(target_positions):
            if 0 <= pos < len(ref) and pos < len(alt_list):
                if alt_list[pos] != ref[pos]:
                    alt_list[pos] = ref[pos]
                    repaired_positions.append(pos)
            elif pos >= len(alt_list) and pos < len(ref):
                alt_list.append(ref[pos])
                repaired_positions.append(pos)

        repaired_seq = "".join(alt_list)
        matches_reference = (repaired_seq == ref)
        remaining_diffs = cls.compare(ref, repaired_seq)

        if matches_reference:
            status = "fully_repaired"
        elif len(repaired_positions) > 0:
            status = "partially_repaired"
        else:
            status = "unrepairable_without_valid_positions"

        event = cls.log_event(
            operation_type="reference_guided_repair",
            initial_sequence=alt,
            final_sequence=repaired_seq,
            parameters={"authorized_positions": list(target_positions)},
            reference_used=ref,
            detection_result={"original_divergences": len(diffs)},
            repair_result={
                "status": status,
                "repaired_positions": repaired_positions,
                "remaining_divergences": len(remaining_diffs),
                "matches_reference": matches_reference
            }
        )

        return {
            "altered_sequence": alt,
            "reference_sequence": ref,
            "repaired_sequence": repaired_seq,
            "repaired_positions": repaired_positions,
            "matches_reference": matches_reference,
            "status": status,
            "remaining_divergences": len(remaining_diffs),
            "event_id": event["experiment_id"]
        }

    @classmethod
    def simulate_break_repair(
        cls,
        sequence: str,
        break_position: int,
        method: str = "homology_directed",
        reference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        3.3. Roturas de ADN como extension conceptual (Double-strand break model).
        Representa una rotura en una posicion definida.
        Compara dos resultados abstractos:
        - 'homology_directed' (HDR): reconstruccion guiada por secuencia homologa disponible.
        - 'end_joining' (NHEJ): union de extremos sin plantilla completa (posible delecion/cicatriz).
        """
        clean = sequence.upper().strip()
        if not cls.validate(clean):
            raise ValueError("Secuencia invalida para rotura de ADN")

        if break_position <= 0 or break_position >= len(clean):
            raise ValueError(f"Posicion de rotura {break_position} invalida (longitud: {len(clean)})")

        frag_left = clean[:break_position]
        frag_right = clean[break_position:]
        m_lower = method.lower()

        if m_lower in ("homology_directed", "hdr", "homologous"):
            if not reference:
                raise ValueError("La reparacion guiada por homologia requiere una secuencia de referencia o plantilla homologa.")
            ref_clean = reference.upper().strip()
            if not cls.validate(ref_clean):
                raise ValueError("Secuencia de referencia homologa invalida")
            repaired_seq = ref_clean
            scar = "none_homology_fidelity"
            desc = "Reconstruccion de alta fidelidad asistida por plantilla homologa (análogo a HDR)."
            status = "repaired_high_fidelity"

        elif m_lower in ("end_joining", "nhej", "non_homologous"):
            # Modelo abstracto NHEJ: union de extremos sin plantilla completa
            scar_type = random.choice(["direct_ligation", "micro_deletion"])
            if scar_type == "micro_deletion" and len(frag_left) > 1:
                repaired_seq = frag_left[:-1] + frag_right
                scar = f"micro_deletion_at_{break_position-1}"
            else:
                repaired_seq = frag_left + frag_right
                scar = "direct_blunt_ligation"
            desc = "Union directa de extremos rotos sin plantilla (análogo a NHEJ). Propenso a cicatriz mutacional."
            status = "repaired_prone_to_scar"
        else:
            raise ValueError(f"Metodo de reparacion de rotura desconocido: {method}")

        event = cls.log_event(
            operation_type="dna_break_and_repair",
            initial_sequence=clean,
            final_sequence=repaired_seq,
            parameters={
                "break_position": break_position,
                "repair_method": m_lower,
                "scar_type": scar
            },
            reference_used=reference,
            detection_result={"break_fragments": [frag_left, frag_right]},
            repair_result={"status": status, "matches_initial": (repaired_seq == clean)}
        )

        return {
            "initial_sequence": clean,
            "break_position": break_position,
            "fragments": [frag_left, frag_right],
            "repair_method": m_lower,
            "repaired_sequence": repaired_seq,
            "scar": scar,
            "description": desc,
            "status": status,
            "matches_initial": (repaired_seq == clean),
            "event_id": event["experiment_id"]
        }

    @classmethod
    def log_event(
        cls,
        operation_type: str,
        initial_sequence: str,
        final_sequence: str,
        parameters: Dict[str, Any],
        reference_used: Optional[str] = None,
        detection_result: Optional[Dict[str, Any]] = None,
        repair_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Seccion 7: Registro de datos de experimentos.
        Guarda el resumen del experimento para trazabilidad estricta.
        """
        import uuid
        import datetime

        event_id = f"EXP-{len(cls._events_log)+1:04d}-{str(uuid.uuid4())[:6].upper()}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        record = {
            "experiment_id": event_id,
            "timestamp": timestamp,
            "operation_type": operation_type,
            "initial_sequence": initial_sequence,
            "final_sequence": final_sequence,
            "parameters": parameters,
            "reference_used": reference_used,
            "detection_result": detection_result or {},
            "repair_result": repair_result or {},
            "code_version": "v1.1-phase1-closed",
            "model_assumptions": (
                "Simulacion didactica computacional basada en reglas abstractas de nucleotidos. "
                "No reproduce la cinetica molecular enzimatica completa (polimerasas, nucleasas o ligasas)."
            )
        }
        cls._events_log.append(record)
        return record

    @classmethod
    def get_events(cls, limit: int = 50) -> List[Dict[str, Any]]:
        return list(reversed(cls._events_log[-limit:]))

    _saved_experiments: List[Dict[str, Any]] = []

    @classmethod
    def _get_storage_file(cls) -> str:
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "saved_experiments.json")

    @classmethod
    def _load_saved_from_disk(cls):
        import os, json
        filepath = cls._get_storage_file()
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    cls._saved_experiments = json.load(f)
            except Exception:
                pass

    @classmethod
    def _persist_saved_to_disk(cls):
        import json
        filepath = cls._get_storage_file()
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(cls._saved_experiments, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    @classmethod
    def save_full_experiment(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Guarda un informe integral y completo del experimento de laboratorio:
        secuencia inicial, copia, mutación aplicada, detección, reparación, secuencia final y diff.
        """
        import uuid, datetime
        if not cls._saved_experiments:
            cls._load_saved_from_disk()

        exp_id = data.get("experiment_id")
        if not exp_id:
            exp_id = f"EXP-{len(cls._saved_experiments)+1:04d}-{str(uuid.uuid4())[:6].upper()}"

        record = {
            "experiment_id": exp_id,
            "name": data.get("name") or f"Ensayo genético {exp_id}",
            "created_at": data.get("created_at") or datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "initial_sequence": data.get("initial_sequence", ""),
            "working_copy": data.get("working_copy", ""),
            "mutation_applied": data.get("mutation_applied") or {},
            "altered_sequence": data.get("altered_sequence", ""),
            "detection_result": data.get("detection_result") or {},
            "repair_applied": data.get("repair_applied") or {},
            "final_sequence": data.get("final_sequence", ""),
            "diff_result": data.get("diff_result") or {},
            "status": data.get("status", "completed"),
            "notes": data.get("notes") or "Registro completo del experimento guardado por el usuario en BioSim Lab.",
            "code_version": "v1.1-phase1-closed"
        }

        # Actualizar si ya existe con ese ID, o añadir al inicio
        existing_idx = next((i for i, x in enumerate(cls._saved_experiments) if x["experiment_id"] == exp_id), None)
        if existing_idx is not None:
            cls._saved_experiments[existing_idx] = record
        else:
            cls._saved_experiments.insert(0, record)

        cls._persist_saved_to_disk()

        # También registrar en events_log para auditoría
        cls.log_event(
            operation_type="full_experiment_save",
            initial_sequence=record["initial_sequence"],
            final_sequence=record["final_sequence"],
            parameters={"saved_name": record["name"]},
            reference_used=record["initial_sequence"],
            detection_result=record["detection_result"],
            repair_result=record["repair_applied"]
        )
        return record

    @classmethod
    def list_saved_experiments(cls) -> List[Dict[str, Any]]:
        if not cls._saved_experiments:
            cls._load_saved_from_disk()
        return cls._saved_experiments

    @classmethod
    def get_saved_experiment(cls, exp_id: str) -> Optional[Dict[str, Any]]:
        if not cls._saved_experiments:
            cls._load_saved_from_disk()
        return next((x for x in cls._saved_experiments if x["experiment_id"] == exp_id), None)

dna_engine = DNAEngine()

