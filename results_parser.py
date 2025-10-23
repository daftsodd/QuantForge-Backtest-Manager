"""
Results Parser for extracting and structuring backtest results.
"""
import os
from pathlib import Path
import pandas as pd
from PIL import Image
import json


class ResultsParser:
    """Parses backtest results from output files."""
    
    def __init__(self):
        self.cached_results = {}
    
    def parse_results(self, script_path):
        """Parse results for a given script.
        
        Returns:
            dict: {
                'statistics': dict of key metrics,
                'tables': list of (name, DataFrame) tuples,
                'images': list of (name, path) tuples,
                'metadata': execution metadata if available
            }
        """
        script_dir = Path(script_path).parent
        script_name = Path(script_path).stem
        
        # Check cache
        cache_key = f"{script_path}_{os.path.getmtime(script_path)}"
        if cache_key in self.cached_results:
            return self.cached_results[cache_key]
        
        results = {
            'statistics': {},
            'tables': [],
            'images': [],
            'metadata': None
        }
        
        # Load execution metadata
        metadata_file = script_dir / f"{script_name}_execution.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    results['metadata'] = json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
        
        # Find and parse Excel files
        for file in script_dir.glob("*.xlsx"):
            try:
                df = pd.read_excel(file)
                results['tables'].append((file.stem, df))
                
                # Extract key statistics if available
                if not df.empty:
                    self._extract_statistics(df, results['statistics'])
            except Exception as e:
                print(f"Error reading {file}: {e}")
        
        # Find image files
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            for file in script_dir.glob(ext):
                try:
                    # Verify it's a valid image
                    with Image.open(file) as img:
                        results['images'].append((file.stem, str(file)))
                except Exception as e:
                    print(f"Error loading image {file}: {e}")
        
        # Cache results
        self.cached_results[cache_key] = results
        
        return results
    
    def _extract_statistics(self, df, statistics):
        """Extract key statistics from a DataFrame."""
        # Look for common column names in backtest results
        stat_columns = [
            'Total_Profit_%', 'Sharpe_Ratio', 'Sortino_Ratio', 'Omega_Ratio',
            'Max_Drawdown_%', 'Number_of_Trades', 'Final_Portfolio_Value',
            'Win_Rate', 'Profit_Factor', 'Average_Trade'
        ]
        
        for col in stat_columns:
            if col in df.columns:
                try:
                    # Get statistics for this column
                    values = pd.to_numeric(df[col], errors='coerce').dropna()
                    if not values.empty:
                        statistics[f"{col}_mean"] = values.mean()
                        statistics[f"{col}_max"] = values.max()
                        statistics[f"{col}_min"] = values.min()
                        statistics[f"{col}_std"] = values.std()
                except Exception:
                    pass
        
        # Try to find the best performing configuration
        if 'Total_Profit_%' in df.columns:
            try:
                best_idx = df['Total_Profit_%'].idxmax()
                best_row = df.loc[best_idx]
                statistics['best_config'] = best_row.to_dict()
            except Exception:
                pass
    
    def clear_cache(self):
        """Clear the results cache."""
        self.cached_results.clear()
    
    def get_execution_summary(self, script_path):
        """Get a quick summary of the last execution."""
        script_dir = Path(script_path).parent
        script_name = Path(script_path).stem
        metadata_file = script_dir / f"{script_name}_execution.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            return {
                'success': metadata.get('success', False),
                'elapsed_time': metadata.get('elapsed_time', 0),
                'timestamp': metadata.get('timestamp', 0)
            }
        except Exception:
            return None

