import pandas as pd
import json
from tqdm import tqdm
import random
import numpy as np

tqdm.pandas()


class AdditionalDataParser:
    def __init__(self, df, json_column="Adj Event Data", sample_frac=0.05):
        self.df = df.copy()
        self.json_column = json_column
        self.sample_frac = sample_frac
        self._parsed_column = "Parsed Event Data"
        self._flat_column = "Flat Dict"

    def deep_json_parse(self, data):
        if isinstance(data, str):
            data = data.strip()
            if (data.startswith("{") and data.endswith("}")) or (data.startswith("[") and data.endswith("]")):
                try:
                    parsed = json.loads(data)
                    return self.deep_json_parse(parsed)
                except json.JSONDecodeError:
                    return data
            return data
        elif isinstance(data, dict):
            return {key: self.deep_json_parse(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.deep_json_parse(item) for item in data]
        else:
            return data

    def flatten_json(self, y):
        out = {}

        def flatten(x, name=''):
            if isinstance(x, dict):
                for a in x:
                    flatten(x[a], f'{name}{a}.')
            elif isinstance(x, list):
                out[name[:-1]] = x
                for i, a in enumerate(x):
                    flatten(a, f'{name}{i}.')
            else:
                out[name[:-1]] = x

        flatten(y)
        return out

    def parse_and_flatten(self):
        print("🔄 Parsing and flattening JSON...")
        self.df[self._parsed_column] = self.df[self.json_column].progress_apply(lambda raw: self.deep_json_parse(json.loads(raw)))
        self.df[self._flat_column] = self.df[self._parsed_column].apply(self.flatten_json)
        flat_df = self.df[self._flat_column].apply(pd.Series)
        self.df = pd.concat([self.df.drop(columns=[self._flat_column, self._parsed_column]), flat_df], axis=1)
        print("✅ Done flattening.")

    def compare_flattened_with_original(self, flat_row, original_parsed_json):
        issues = []

        def recurse(d, path=''):
            if isinstance(d, dict):
                for k, v in d.items():
                    recurse(v, f"{path}{k}.")
            elif isinstance(d, list):
                key = path[:-1]
                if key not in flat_row:
                    issues.append((key, "missing in flattened"))
                elif flat_row[key] != d:
                    issues.append((key, f"Expected: {d}, Found: {flat_row[key]}"))
            else:
                key = path[:-1]
                if key not in flat_row:
                    issues.append((key, "missing in flattened"))
                elif flat_row[key] != d:
                    issues.append((key, f"Expected: {d}, Found: {flat_row[key]}"))
        recurse(original_parsed_json)
        return issues

    def run_sanity_check(self):
        print(f"\n🧪 Running sanity check on {int(self.sample_frac * 100)}% of rows...")
        sample = self.df.sample(frac=self.sample_frac, random_state=42)
        pass_count = 0

        for idx in sample.index:
            raw = self.df.loc[idx, self.json_column]
            parsed = self.deep_json_parse(json.loads(raw))
            flattened = self.flatten_json(parsed)
            mismatches = self.compare_flattened_with_original(flattened, parsed)
            if mismatches:
                print(f"\n❌ Row {idx} mismatches:")
                for m in mismatches[:5]:
                    print(" -", m[0], "→", m[1])
            else:
                print(f"✅ Row {idx} passed.")
                pass_count += 1

        print(f"\n🎉 Sanity check complete. Passed {pass_count}/{len(sample)} rows.")

    def get_df(self):
        return self.df

