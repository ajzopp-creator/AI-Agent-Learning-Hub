# =============================================================================
# xml_parser.py - Shared TOS XML Export Parser
# =============================================================================
# Location: shared_resources/python_utils/xml_parser.py
# Used by: P_300, P_110, P_010 projects
# =============================================================================

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd


def parse_history_xml(xml_path: str) -> Dict:
    """
    Parse TOS History Grid XML export file.
    
    Args:
        xml_path: Path to the XML file (e.g., History Grid (SPY)_v2.xml)
    
    Returns:
        Dictionary containing parsed data with keys:
        - 'symbol': Stock symbol
        - 'data': List of dictionaries with OHLCV data
        - 'metadata': Additional file metadata
    
    Example:
        from shared_resources.python_utils.xml_parser import parse_history_xml
        
        data = parse_history_xml('data/xml_exports/History Grid (SPY)_v2.xml')
        df = pd.DataFrame(data['data'])
    """
    
    path = Path(xml_path)
    if not path.exists():
        raise FileNotFoundError(f"XML file not found: {xml_path}")
    
    tree = ET.parse(path)
    root = tree.getroot()
    
    # Extract symbol from filename (e.g., "History Grid (SPY)_v2.xml" -> "SPY")
    filename = path.stem
    symbol = None
    if '(' in filename and ')' in filename:
        symbol = filename.split('(')[1].split(')')[0]
    
    result = {
        'symbol': symbol,
        'data': [],
        'metadata': {
            'source_file': str(path.name),
            'full_path': str(path.absolute())
        }
    }
    
    # Parse based on TOS XML structure
    for row in root.findall('.//Row'):
        row_data = {}
        for cell in row:
            tag = cell.tag
            value = cell.text
            
            # Convert numeric values
            if value and tag in ['Open', 'High', 'Low', 'Close', 'Volume', 'Price']:
                try:
                    value = float(value.replace(',', '')) if '.' in value else int(value.replace(',', ''))
                except ValueError:
                    pass
            
            row_data[tag] = value
        
        if row_data:
            result['data'].append(row_data)
    
    return result


def parse_multiple_xmls(xml_folder: str, pattern: str = "*.xml") -> Dict[str, Dict]:
    """
    Parse multiple XML files from a folder.
    
    Args:
        xml_folder: Path to folder containing XML files
        pattern: Glob pattern for matching files (default: *.xml)
    
    Returns:
        Dictionary with symbols as keys and parsed data as values
    """
    
    folder = Path(xml_folder)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {xml_folder}")
    
    results = {}
    for xml_file in folder.glob(pattern):
        try:
            parsed = parse_history_xml(str(xml_file))
            key = parsed['symbol'] or xml_file.stem
            results[key] = parsed
        except Exception as e:
            print(f"Warning: Failed to parse {xml_file.name}: {e}")
    
    return results


def xml_to_dataframe(xml_path: str) -> pd.DataFrame:
    """
    Convenience function to directly get a DataFrame from XML.
    
    Args:
        xml_path: Path to the XML file
    
    Returns:
        pandas DataFrame with the parsed data
    """
    parsed = parse_history_xml(xml_path)
    df = pd.DataFrame(parsed['data'])
    df.attrs['symbol'] = parsed['symbol']
    return df


# =============================================================================
# Module test
# =============================================================================
if __name__ == "__main__":
    print("XML Parser Utility - Test Mode")
    print("=" * 50)
    
    test_path = Path(__file__).parent.parent.parent / "projects" / "P_300_Vantage_Point_Pattern_Recognition" / "data" / "xml_exports"
    
    if test_path.exists():
        print(f"Found folder: {test_path}")
        xml_files = list(test_path.glob("*.xml"))
        print(f"XML files found: {len(xml_files)}")
        
        for f in xml_files:
            print(f"\n  Parsing: {f.name}")
            try:
                data = parse_history_xml(str(f))
                print(f"    Symbol: {data['symbol']}")
                print(f"    Rows: {len(data['data'])}")
            except Exception as e:
                print(f"    Error: {e}")
    else:
        print(f"Test folder not found: {test_path}")