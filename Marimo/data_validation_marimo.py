import marimo

__generated_with = "0.10.9"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # 資料驗證

        ## 匯入欲進行驗證的資料
        """
    )
    return


@app.cell
def _(mo):
    f = mo.ui.file(kind="area", filetypes=['.csv'])
    return (f,)


@app.cell
def _(f):
    f
    return


@app.cell
def _(f, pl):
    df = pl.read_csv(f.contents() if f is not None else 'Tutorial_Data/penguins_v.csv')
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""前五筆資料如下：""")
    return


@app.cell
def _(df):
    df.head()
    return


@app.cell
def _():
    # initial_code = """# implement class P below
    # class P(pt.Model):
    #     ...
    # """

    # editor = mo.ui.code_editor(
    #     value=initial_code,
    #     language='python'
    # )

    # editor
    return


@app.cell
def _(mo):
    def create_column_config(col_name: str, inferred_type: str):
        """Create configuration UI elements for a single column"""
        return {
            "type": mo.ui.dropdown(
                options=["Literal", "int", "float", "str", "bool"],
                value=inferred_type,
                label="Data Type"
            ),
            "optional": mo.ui.checkbox(label="Optional", value=False),
            "unique": mo.ui.checkbox(label="Unique", value=False),
            "min_value": mo.ui.number(label="Min value", value=None),
            "max_value": mo.ui.number(label="Max value", value=None),
            "literal_values": mo.ui.text_area(label="Literal values (one per line)", value="", placeholder="Only for Literal type", full_width=True),
            "constraints": mo.ui.text_area(label="Constraints", value="", placeholder="Enter constraints here, written in Polars expressions", full_width=True)
        }
    return (create_column_config,)


@app.cell
def _(create_column_config, df, dtype_mapping, mo):
    # Create separate configuration for each column
    all_forms = []

    # Store each column's configuration in a separate cell
    columns_config = {}

    for c in df.columns:
        inferred_type = dtype_mapping.get(df[c].dtype, 'str')
        controls = create_column_config(c, inferred_type)
        columns_config[c] = controls

        all_forms.append(
            mo.vstack([
            mo.md(f"### {c}"),
            controls["type"],
            controls["optional"],
            controls["unique"],
            controls["min_value"],
            controls["max_value"],
            controls["literal_values"],
            controls["constraints"],
            mo.md("---")
            ])
        )
    return all_forms, c, columns_config, controls, inferred_type


@app.cell
def _(all_forms, mo):
    run = mo.ui.run_button(label="Generate Model")

    # Combine all elements using mo.vstack
    interface = mo.vstack([
        mo.md("""---
        
        ## 欄位設定
        """),
        *all_forms,
        run,
    ])
    return interface, run


@app.cell
def _(interface):
    # Run the interface
    interface
    return


@app.cell
def _(Dict):
    def generate_model_code(column_configs: Dict) -> str:
        code_lines = ["class P(pt.Model):"]

        for col, config in column_configs.items():
            field_def = f"    {col}: "
            field_type = config["type"]

            if field_type == "Literal":
                values = [f"'{val.strip()}'" for val in config["literal_values"].split('\n') if val.strip()]
                if values:
                    field_def += f"Literal[{', '.join(values)}]"
                else:
                    field_def += 'str'
            else:
                field_def += field_type

            # Add field configurations
            field_configs = []
            if config["unique"]:
                field_configs.append('unique=True')

            if not field_type.startswith('Optional'):
                if config["min_value"] is not None:
                    field_configs.append(f'ge={config["min_value"]}')
                if config["max_value"] is not None:
                    field_configs.append(f'le={config["max_value"]}')
                if config["constraints"] != "":
                    field_configs.append(f'constraints={config["constraints"]}')

            if field_configs:
                field_def += f" = pt.Field({', '.join(field_configs)})"

            code_lines.append(field_def)

        return "\n".join(code_lines)
    return (generate_model_code,)


@app.cell(hide_code=True)
def _(columns_config, df, generate_model_code, mo, run):
    code = ''

    if run.value:
        # Collect configurations
        configs = {}
        for col in df.columns:
            cont = columns_config[col]
            base_type = cont["type"].value

            final_type = f"Optional[{base_type}]" if cont["optional"].value else base_type

            configs[col] = {
                "type": final_type,
                "unique": cont["unique"].value,
                "min_value": cont["min_value"].value,
                "max_value": cont["max_value"].value,
                "literal_values": cont["literal_values"].value,
                "constraints": cont["constraints"].value
            }

        code = generate_model_code(configs)

    mo.md(f"""## Preview:

    ```python
    {code}
    ```
    """)
    return base_type, code, col, configs, cont, final_type


@app.cell
def _(mo):
    gen = mo.ui.run_button(label="Validate Data")
    gen
    return (gen,)


@app.cell
def _(mo):
    mo.md(f"""## Validation Results:""")
    return


@app.cell
def _(ErrorReporter, P, code, df, gen, mo):
    if gen.value:
        try:
            exec(code)
            v = ErrorReporter(P, df)
        except SyntaxError as e:
            mo.output.replace(f"SyntaxError: {e}")
        except NameError as e:
            mo.output.replace(f"NameError: {e}")
    return (v,)


@app.cell
def _(v):
    try:
        report = v.report()
    except:
        report = None

    report
    return (report,)


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import patito as pt
    from typing import Literal, Optional, Dict, List
    import re
    return Dict, List, Literal, Optional, mo, pl, pt, re


@app.cell
def _(Dict, List, pl, re):
    class ErrorReporter:
        def __init__(self, validator_class, df: pl.DataFrame):
            self.validator = validator_class
            self.df = df
            self.error_report = self._val()

        def _val(self):
            try:
                self.validator.validate(self.df)
                return 'Pass'
            except Exception as e:
                return self._get_error_report(e.errors(), self.df.columns)

        def _get_error_report(self, error_list: List[Dict], col_list: List[str]) -> pl.DataFrame:
            """
            Parse a list of error items into a DataFrame with columns: column, pass, failed_count, msg, type

            Args:
                error_list (List[Dict]): List of error items
                col_list (List[str]): List of column names

            Returns:
                pl.DataFrame: DataFrame with parsed error information
            """
            column_list = []
            failed_count_list = []
            msg_list = []
            type_list = []

            for error in error_list:
                # Extract column name from loc tuple
                column = error['loc'][0]

                # Extract failed count if present in msg
                failed_count = None
                msg = error['msg']
                count_match = re.match(r'^\d+', msg)
                if count_match:
                    failed_count = int(count_match.group(0))

                column_list.append(column)
                failed_count_list.append(failed_count)
                msg_list.append(msg)
                type_list.append(error['type'])

            # Create DataFrame and order columns
            df_error = pl.DataFrame({
                'column': column_list,
                'pass': False,
                'failed_count': failed_count_list,
                'msg': msg_list,
                'type': type_list
            })

            df_error = df_error.join(pl.DataFrame({'column': col_list}), on='column', how='full')\
                            .with_columns(
                                pl.when(pl.col('pass').is_not_null())
                                        .then(pl.col('pass'))
                                        .otherwise(True).alias('pass'),
                                pl.when(pl.col('column').is_not_null())
                                        .then(pl.col('column'))
                                        .otherwise(pl.col('column_right')).alias('column'),
                                pl.when(pl.col('failed_count').is_not_null())
                                        .then(pl.col('failed_count'))
                                        .otherwise(0).alias('failed_count')
                                            )\
                            .drop('column_right')

            return df_error

        def report(self) -> pl.DataFrame:
            return self.error_report

        def summary(self) -> pl.DataFrame:
            if type(self.error_report) == 'str':
                return self.error_report

            return self.error_report.group_by('column').agg([
                pl.col('pass').all().alias('pass')
            ])

        def count(self) -> pl.DataFrame:
            if type(self.error_report) == 'str':
                return 0

            return self.error_report.group_by('column').agg([
                pl.col('pass').count().alias('count')
            ])

        def __str__(self):
            return str(self.error_report)
    return (ErrorReporter,)


@app.cell
def _(pl):
    dtype_mapping = {
        pl.Int8: 'int',
        pl.Int16: 'int',
        pl.Int32: 'int',
        pl.Int64: 'int',
        pl.UInt8: 'int',
        pl.UInt16: 'int',
        pl.UInt32: 'int',
        pl.UInt64: 'int',
        pl.Float32: 'float',
        pl.Float64: 'float',
        pl.Decimal: 'float',
        pl.String: 'str',
        pl.Boolean: 'bool',
    }
    return (dtype_mapping,)


if __name__ == "__main__":
    app.run()
