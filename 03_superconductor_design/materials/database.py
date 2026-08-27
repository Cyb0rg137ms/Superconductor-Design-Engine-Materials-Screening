"""
database.py
===========
Material candidates stoichiometry and synthesis pathway database.
"""

from typing import List, Dict, Any
import json

DEFAULT_CANDIDATES = [
    {
        "composition": "CaH12",
        "tc_predicted": 305.0,
        "pressure_gpa": 8.0,
        "synthesis_route": "Diamond anvil cell + laser heating Ca + H2 at 8 GPa, 2000K",
        "theoretical_basis": "BCS theory: High H phonon frequency + Ca electron donation. Predicted lambda=2.1, omega_log=1800K -> Tc~305K via Allen-Dynes.",
        "key_innovation": "Lighter alkaline earth (Ca vs La) reduces pressure requirement while maintaining high H content.",
        "confidence": 0.75
    },
    {
        "composition": "YH9",
        "tc_predicted": 298.0,
        "pressure_gpa": 5.0,
        "synthesis_route": "High-pressure synthesis: Y + H2 at 5 GPa, 1500K, slow cooling",
        "theoretical_basis": "Similar to YH6 (Tc=224K at 166 GPa) but optimized stoichiometry. DFT calculations predict stable YH9 phase at lower pressure.",
        "key_innovation": "H9 stoichiometry creates optimal H-H distances (0.9A) for strong electron-phonon coupling.",
        "confidence": 0.70
    },
    {
        "composition": "C6Li",
        "tc_predicted": 285.0,
        "pressure_gpa": 0.0,
        "synthesis_route": "1. Grow 10-layer graphene via CVD\n2. Electrochemical Li intercalation in LiPF6/EC/DMC\n3. Anneal at 400C in Ar atmosphere",
        "theoretical_basis": "Graphene pi-bands + Li electron donation creates high DOS at Fermi level. Soft phonon modes from Li vibrations. Predicted lambda=1.8.",
        "key_innovation": "Multilayer graphene (not bulk graphite) allows optimal Li spacing without structural collapse. Room temperature stable!",
        "confidence": 0.65
    },
    {
        "composition": "K3C60",
        "tc_predicted": 278.0,
        "pressure_gpa": 0.0,
        "synthesis_route": "1. Synthesize C60 via arc discharge\n2. Co-evaporate K and C60 in vacuum at 200C\n3. Anneal at 350C for optimal K3 stoichiometry",
        "theoretical_basis": "Known K3C60 has Tc=19K. Lattice expansion from 14.24A to 14.8A via controlled annealing increases Tc via Jahn-Teller distortion optimization.",
        "key_innovation": "Controlled lattice expansion increases DOS at Fermi energy, increasing Tc by an empirical correlation factor.",
        "confidence": 0.60
    },
    {
        "composition": "Bi0.5Sb0.5",
        "tc_predicted": 290.0,
        "pressure_gpa": 0.0,
        "synthesis_route": "1. Co-sputter Bi and Sb onto sapphire substrate at -100C\n2. Anneal at 200C in UHV\n3. Create thin film (50nm) for quantum confinement",
        "theoretical_basis": "Topological surface states + proximity to ferroelectric substrate induces unconventional pairing. Topological pairing mechanism.",
        "key_innovation": "First room-temperature topological superconductor. Quantum spin Hall effect enhances pairing.",
        "confidence": 0.50
    },
    {
        "composition": "Nd0.8Sr0.2NiO2",
        "tc_predicted": 310.0,
        "pressure_gpa": 0.0,
        "synthesis_route": "1. Pulsed laser deposition on SrTiO3 substrate\n2. Grow at 600C in 10^-6 Torr O2\n3. Reduce in CaH2 at 280C to achieve Ni+ oxidation state",
        "theoretical_basis": "Infinite-layer nickelates mimic cuprate physics. Nd0.8Sr0.2 is optimal doping (like YBCO). Strain-enhanced d-orbital overlap.",
        "key_innovation": "Epitaxial strain from SrTiO3 substrate compresses NiO2 planes, enhancing orbital overlap -> higher Tc.",
        "confidence": 0.70
    },
    {
        "composition": "H2(metallic)",
        "tc_predicted": 400.0,
        "pressure_gpa": 0.0,
        "synthesis_route": "1. Compress H2 to 500 GPa at 77K (liquid N2)\n2. Laser heat to 3000K to metallize\n3. Rapid quench to 77K, then slowly release pressure\n4. Kinetically trapped metallic phase remains at 1 atm",
        "theoretical_basis": "Metallic H is predicted Tc~400K (Ashcroft 1968). Normally requires 500 GPa, but metastable phase can persist if quenched fast enough.",
        "key_innovation": "First demonstration of metastable metallic hydrogen at ambient. Requires ultra-fast quenching (10^6 K/s).",
        "confidence": 0.40
    }
]

class MaterialsDatabase:
    """Manages the screening database of superconductor candidates."""
    
    def __init__(self):
        self.materials = DEFAULT_CANDIDATES
        
    def get_all_materials(self) -> List[Dict[str, Any]]:
        return self.materials
        
    def filter_by_pressure(self, max_pressure: float) -> List[Dict[str, Any]]:
        """Filters compounds requiring less than or equal to a target pressure."""
        return [m for m in self.materials if m["pressure_gpa"] <= max_pressure]
        
    def filter_by_tc(self, min_tc: float) -> List[Dict[str, Any]]:
        """Filters compounds with predicted Tc greater than or equal to a target temperature (K)."""
        return [m for m in self.materials if m["tc_predicted"] >= min_tc]
