# -*- coding: utf-8 -*-
"""
UUID migration table for legacy ecoinvent 3.5 biosphere flows.

The swolfpy input data (LCI CSVs and process model data) was built against
ecoinvent 3.5.  Some biosphere3 flows were renamed or replaced in later
ecoinvent releases bundled with bw2io 0.9.x.

``BIOSPHERE_UUID_MIGRATION`` maps old (stale) biosphere3 ``code`` values to
their current equivalents so that swolfpy can write valid Brightway2 databases
without losing any exchanges.
"""

from typing import Dict, Tuple

# Maps old biosphere3 code → new biosphere3 code.
# Keys / values are bare UUID strings (without the "biosphere3" database prefix).
BIOSPHERE_UUID_MIGRATION: Dict[str, str] = {
    # Ethene → Ethylene  (air, unspecified)
    "9c2a7dc9-8b1f-46ba-bc16-0d761a4f6016": "90f722bf-cb9b-571a-88fc-34286632bdc4",
    # Hydrogen chloride → Hydrochloric acid  (air, unspecified)
    "c941d6d0-a56c-4e6c-95de-ac685635218d": "c9a8073a-8a19-5b9b-a120-7d549563b67b",
    # Methane (air, urban) → Methane, fossil  (air, urban)
    "b53d3744-3629-4219-be20-980865e54031": "5f7aad3d-566c-4d0d-ad59-e765f971aa0f",
    # Gangue, bauxite, in ground → Gangue  (natural resource, in ground)
    "43b2649e-26f8-400d-bc0a-a0667e850915": "0d218f74-181d-49b6-978c-8af836611102",
    # Carfentrazone ethyl ester → Carfentrazone-ethyl  (soil, agricultural)
    "d07867e3-66a8-4454-babd-78dc7f9a21f8": "91d68678-7ed7-417a-86a7-a486c7b8a973",
    # Haloxyfop-(R) methylester → Haloxyfop-P-methyl  (soil, agricultural)
    "66a6dad0-e450-4206-88e1-f823a04f8b1d": "a058168e-9a1e-5126-80b6-2d202e746835",
    # Quizalofop ethyl ester → Quizalofop-ethyl  (soil, agricultural)
    "f9c73aca-3d5c-4072-81dd-b8e0643530a6": "9ae11925-3df9-5fde-b7af-1627c0818347",
    # Iron (water, ground-) → Iron ion  (water, ground-)
    "e3043a7f-5347-4c7b-89ee-93f11b2f6d9b": "33fd8342-58e7-45c9-ad92-0951c002c403",
    # Nickel, ion (water, ground-) → Nickel II  (water, ground-)
    "e030108f-2125-4bcb-a73b-ad72130fcca3": "56815b4f-6138-4e0b-9fac-c94fd6b102b3",
    # Potassium, ion (water, ground-) → Potassium I  (water, ground-)
    "a07b8a8c-8cab-4656-a82f-310e8069e323": "c21a1397-82dc-427a-a6cb-c790ba2626f4",
    # Sulfate, ion (water, ground-) → Sulfate  (water, ground-)
    "b8c794de-ac20-47f6-ae87-84d91e95da93": "31eacbfc-683a-4d36-afc1-80dee42a3b94",
}

# Reverse mapping: new code → old code.
# Used by tests to reconcile migrated DB keys with legacy report keys.
_REVERSE_MIGRATION: Dict[str, str] = {v: k for k, v in BIOSPHERE_UUID_MIGRATION.items()}


def migrate_biosphere_key(key: Tuple[str, str]) -> Tuple[str, str]:
    """
    Remap a biosphere3 ``(database, code)`` key to its current equivalent.

    If the key is not in the migration table it is returned unchanged.

    :param key: A biosphere3 key tuple ``("biosphere3", code)``
    :type key: tuple[str, str]

    :return: The same key or its migrated replacement
    :rtype: tuple[str, str]
    """
    if isinstance(key, tuple) and len(key) == 2 and key[0] == "biosphere3":
        new_code = BIOSPHERE_UUID_MIGRATION.get(key[1])
        if new_code:
            return ("biosphere3", new_code)
    return key


def original_biosphere_key(key: Tuple[str, str]) -> Tuple[str, str]:
    """
    Reverse-map a current biosphere3 key to its original (pre-migration) key.

    Used by tests to look up exchange amounts in process model reports that
    still carry legacy ecoinvent 3.5 UUIDs, while the Brightway2 database was
    written with the migrated (current) UUIDs.

    :param key: A biosphere3 key tuple ``("biosphere3", code)``
    :type key: tuple[str, str]

    :return: The original key (before UUID migration) or the key unchanged
    :rtype: tuple[str, str]
    """
    if isinstance(key, tuple) and len(key) == 2 and key[0] == "biosphere3":
        old_code = _REVERSE_MIGRATION.get(key[1])
        if old_code:
            return ("biosphere3", old_code)
    return key
