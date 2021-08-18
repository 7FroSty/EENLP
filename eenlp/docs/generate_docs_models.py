import mdformat
import pandas as pd
import yaml
from pyprojroot import here

from eenlp.docs.languages import languages

# TODO This code is a mess. Clean it up.
from eenlp.docs.model_types import cases, corpora, types

categories = [
    "multilingual-global",
    "multilingual-local",
    "single-language",
    "other",
]

category_captions = {
    "multilingual-global": "multilingual",
    "multilingual-local": "several languages",
    "single-language": "single language models",
    "other": "other",
}

columns = [
    "name",
    "description",
    "type",
    "cased",
    "languages",
    "pre-trained on",
    "links",
    # "huggingface",
    # "type",
    # "paper",
    # "citation",
    # "cased",
    # "pre-trained on",
    # "comments",
]

transformer_base_models = [
    "BERT",
    "RoBERTa",
    "DistilBERT",
    "Electra",
    "ALBERT",
]


def generate():
    df = []
    for dataset in here("docs/data/models/").glob("*.yml"):
        df.append(yaml.safe_load(dataset.read_text()))
    df = pd.DataFrame(df)

    df_o = df

    df = df.explode("languages")

    few_langs_models = [
        x[0]
        for x in df.sort_values("name").groupby(df.index)["languages"].count().items()
        if 1 < x[1] < 10
    ]
    few_langs_models = [
        x
        for x in few_langs_models
        if df.loc[x].iloc[0]["type"]
        in [
            "BERT",
            "RoBERTa",
            "DistilBERT",
            "Electra",
            "ALBERT",
            "XLM-RoBERTa",
            "BERT/Electra(?)",
        ]
    ]

    with open(here("docs/models.md"), "w") as f:
        f.write("# Models\n\n")

        f.write("<table><thead>")
        f.write(
            f'<tr><td rowspan="2"></td><td align="center" width="100">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;multilingual&nbsp;(transformers)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td><td align="center" colspan="{len(few_langs_models)}">several languages (transformers)</td><td align="center" colspan="5">single-language models</td></tr>'
        )
        f.write("<tr><td></td>")

        f.write(
            "".join(
                f'<td align="center">{x}</td>'
                for x in df.loc[few_langs_models]["name"].unique()
            )
        )

        f.write(
            '<td align="center">BERT</td><td align="center">RoBERTa</td><td align="center">DistilBERT</td><td align="center">Electra</td><td align="center">ALBERT</td>'
        )
        f.write("</tr></thead><tbody>\n")

        for i, language in enumerate(languages):
            emoji_name = language["emoji_name"]
            language = language["name"]

            f.write(
                f'<tr><td><a href="#{emoji_name}-{language.lower().replace("/", "")}"><b>:{emoji_name}:&nbsp;{language}</b></a></td>'
            )

            # multilang

            f.write("<td>")
            dff = df[
                (
                    df.apply(
                        lambda x: x["languages"] == language
                        and 10 <= len(df[df.index == x.name])
                        and x["type"]
                        in transformer_base_models + ["mBERT", "XLM-RoBERTa"],
                        axis=1,
                    )
                )
            ]
            f.write(
                " / ".join(
                    sorted(
                        f'<a href="#{x.name.lower().replace(" ", "-")}-multilingual">{x.name}</a>'
                        for x in dff.itertuples()
                    )
                )
            )
            f.write("</td>")

            # few langs
            for i in few_langs_models:
                f.write('<td align="center">')
                dff = df[(df.index == i) & (df["languages"] == language)]
                if len(dff):
                    f.write(
                        f'<a href="#{dff["name"].item().lower().replace(" ", "-")}-{language}">{dff["name"].item()}</a>'
                    )
                f.write("</td>")

            for model_name in transformer_base_models:
                f.write('<td align="center">')
                dff = df[
                    df.apply(
                        lambda x: x["languages"] == language
                        and x["type"] == model_name
                        and len(df[df.index == x.name]) == 1,
                        axis=1,
                    )
                ]
                if len(dff):
                    f.write(
                        " / ".join(
                            sorted(
                                f'<a href="#{x.lower().replace(" ", "-")}-{language}">{x}</a>'
                                for x in dff["name"]
                            )
                        )
                    )
                f.write("</td>")

            f.write("\n")
        f.write("</tbody></table>\n\n")

        f.write("// TODO add legend\n\n")

        for language in ["Multilingual"] + languages:
            if language == "Multilingual":
                emoji_name = "earth_africa"
            else:
                emoji_name = language["emoji_name"]
                language = language["name"]

            f.write(f"## :{emoji_name}: {language}\n\n")

            if language == "Multilingual":
                dff = df_o[df_o["languages"].str.len() >= 10]
            else:
                # dff = df[
                #     (df["languages"] == language)
                #     & (df["category"] != "multilingual-global")
                # ]
                dff = df_o[
                    (df_o["languages"].apply(lambda x: language in x))
                    & (df_o["languages"].str.len() < 10)
                ]

            f.write(
                '<table width="100%"><thead><tr>'
                '<th width="66%">name</th>'
                '<th width="33%">description</th>'
                "<th>type</th>"
                "<th>cased</th>"
                "<th>languages</th>"
                "<th>corpora</th>"
                "<th>links</th>"
                "</tr></thead><tbody>"
            )
            for _, row in sorted(dff.iterrows(), key=lambda x: x[1]["name"]):
                for column in columns:
                    if column == "name":
                        f.write(f"<td")
                        f.write(
                            f' id="{row["name"].lower().replace(" ", "-")}-{language}"'
                        )
                        # if row["URL"] and row["URL"] != "?":
                        #     f.write(f'><a href="{row["URL"]}">{row[column]}</a></td>')
                        # else:
                        f.write(f">{row[column]}</td>")
                    elif column == "languages":
                        f.write("<td>")
                        for x in sorted(
                            df[(df["name"] == row["name"])]["languages"].unique()
                        ):
                            f.write(
                                f'<span title="{x}">:{next(y["emoji_name"] for y in languages if y["name"] == x)}:</span> '
                            )
                        f.write("</td>")
                    elif column == "links":
                        f.write("<td>")
                        if row["paper"] and row["paper"] != "?":
                            f.write(
                                f'<div title="paper"><a href="{row["paper"]}">📄</a></div>'
                            )
                        if row["citation"] and row["citation"] != "?":
                            f.write(
                                f'<div title="citation"><a href="{row["citation"]}">❞</a></div>'
                            )
                        if not pd.isna(row["huggingface"]):
                            f.write(
                                f"<div>"
                                f'<a title="huggingface model card" href="{row["huggingface"]}">🤗️</a> '
                                f"</div>"
                            )
                        f.write("</td>")
                    elif column == "pre-trained on":
                        f.write("<td><ul>")
                        for x in sorted(row["pre-trained on"]):
                            if x != "" and x != "?":
                                if x in corpora:
                                    f.write(
                                        f'<li title="{x}">{corpora[x]["emoji"]}</li>'
                                    )
                                else:
                                    f.write(f'<li title="{x}">{x}</li>')
                        f.write("</ul></td>")
                    elif column == "type":
                        if row["type"] in types:
                            if "image" in types[row["type"]]:
                                f.write(
                                    f'<td align="center"><img width="21px" height="21px" title="{row["type"]}" src="{types[row["type"]]["image"]}"></td>'
                                )
                            else:
                                f.write(
                                    f'<td align="center"><div title="{row["type"]}">{types[row["type"]]["emoji"]}</div></td>'
                                )
                        else:
                            f.write(f"<td>{row['type']}</td>")
                    elif column == "cased":
                        if row["cased"] in cases:
                            f.write(
                                f'<td><div title="{row["cased"]}">{cases[row["cased"]]["emoji"]}</div></td>'
                            )
                        else:
                            f.write(f"<td>{row['cased']}</td>")
                    else:
                        f.write(f"<td>{row[column]}</td>")
                f.write("</tr>\n")
            f.write("</tbody></table>\n\n")
            if language != "Multilingual":
                f.write(
                    "&nbsp;&nbsp;&nbsp;[+ multilingual](#earth_africa-multilingual)"
                )
            f.write("\n\n")

    mdformat.file(here("docs/models.md"), extensions={"gfm"})


if __name__ == "__main__":
    generate()
