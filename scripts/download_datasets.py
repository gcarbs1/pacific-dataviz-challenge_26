#!/usr/bin/env python3
"""Download official Pacific Dataviz Challenge 2026 datasets.

The official list is published at:
https://pacificdatavizchallenge.org/
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOTSTAT_API = "https://stats-nsi-stable.pacificdata.org/rest/data"
USER_AGENT = "pacific-dataviz-challenge-26-data-downloader/1.0"


DOTSTAT_DATASETS = [
    {
        "slug": "environmental_taxes",
        "title": "Environmental taxes",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.ENV_TAXES.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.ENV_TAXES.&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "environmental_taxes_disaggregated",
        "title": "Environmental taxes - disaggregated",
        "agency": "SPC",
        "dataflow": "DF_ENV_TAXES",
        "version": "1.0",
        "key": "A..",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_ENV_TAXES&df[ag]=SPC&df[vs]=1.0&av=true&dq=A..&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "population_growth",
        "title": "Population growth",
        "agency": "SPC",
        "dataflow": "DF_NMDI_POP",
        "version": "1.0",
        "key": "A..NMDI0002._T._T._T..",
        "source_url": "https://stats.pacificdata.org/vis?tm=population%20growth&pg=0&snb=11&df[ds]=ds%3ASPC2&df[id]=DF_NMDI_POP&df[ag]=SPC&df[vs]=1.0&dq=A..NMDI0002._T._T._T..&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "greenhouse_gas_emissions_per_capita",
        "title": "Greenhouse gas emissions per capita",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.GHG_EMI_CAPITA.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.GHG_EMI_CAPITA.&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "crop_yield",
        "title": "Crop yield",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.CROP_YIELD.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.CROP_YIELD.&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "crop_yield_disaggregated",
        "title": "Crop yield - disaggregated",
        "agency": "SPC",
        "dataflow": "DF_AGRICULTURAL_PRODUCTION",
        "version": "1.0",
        "key": "A...",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_AGRICULTURAL_PRODUCTION&df[ag]=SPC&df[vs]=1.0&av=true&dq=A...&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "livestock_yield",
        "title": "Livestock yield",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.LVST_YIELD.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.LVST_YIELD.&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "livestock_yield_disaggregated",
        "title": "Livestock yield - disaggregated",
        "agency": "SPC",
        "dataflow": "DF_AGRICULTURAL_PRODUCTION",
        "version": "1.0",
        "key": "A...",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_AGRICULTURAL_PRODUCTION&df[ag]=SPC&df[vs]=1.0&av=true&dq=A...&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "mean_sea_surface_temperature_anomalies",
        "title": "Mean sea surface temperature anomalies",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.SST_ANOM.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.SST_ANOM.&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "mean_surface_temperature_anomalies",
        "title": "Mean surface temperature anomalies",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.ST_ANOM.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.ST_ANOM.&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "rainfall_anomalies",
        "title": "Rainfall anomalies",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.RAIN_ANOM.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.RAIN_ANOM.&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "climate_altering_land_cover_index",
        "title": "Climate altering land cover index",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.ALT_LAND_COVER.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.ALT_LAND_COVER.&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "sea_level_anomalies",
        "title": "Sea level anomalies",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.SEA_LVL.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.SEA_LVL.&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "tourist_arrivals",
        "title": "Tourist arrivals",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.TRSM_ARR.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.TRSM_ARR.&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "tourist_arrivals_disaggregated",
        "title": "Tourist arrivals - disaggregated",
        "agency": "SPC",
        "dataflow": "DF_TOURISM_ARRIVALS",
        "version": "1.0",
        "key": "A..",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_TOURISM_ARRIVALS&df[ag]=SPC&df[vs]=1.0&av=true&dq=A..&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "red_list_index",
        "title": "Red List Index",
        "agency": "SPC",
        "dataflow": "DF_SDG_15",
        "version": "3.0",
        "key": "A.ER_RSK_LST.........",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=ds%3ASPC2&df[id]=DF_SDG_15&df[ag]=SPC&df[vs]=3.0&dq=A.ER_RSK_LST.........&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "disaster_directly_affected_persons",
        "title": "Number of directly affected persons attributed to disasters",
        "agency": "SPC",
        "dataflow": "DF_SDG_11",
        "version": "3.0",
        "key": "A.VC_DSR_AFFCT.........",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=ds%3ASPC2&df[id]=DF_SDG_11&df[ag]=SPC&df[vs]=3.0&dq=A.VC_DSR_AFFCT.........&pd=,&to[TIME_PERIOD]=false&lb=bt",
    },
    {
        "slug": "direct_disaster_economic_loss",
        "title": "Direct disaster economic loss",
        "agency": "SPC",
        "dataflow": "DF_SDG_11",
        "version": "3.0",
        "key": "A.VC_DSR_AALT...._T.....",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=ds%3ASPC2&df[id]=DF_SDG_11&df[ag]=SPC&df[vs]=3.0&dq=A.VC_DSR_AALT...._T.....&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "tuberculosis_incidence_per_100000_population",
        "title": "Tuberculosis incidence per 100,000 population",
        "agency": "SPC",
        "dataflow": "DF_SDG_03",
        "version": "3.0",
        "key": "A.SH_TBS_INCD.........",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=ds%3ASPC2&df[id]=DF_SDG_03&df[ag]=SPC&df[vs]=3.0&dq=A.SH_TBS_INCD.........&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "renewable_energy_share_total_final_energy_consumption",
        "title": "Renewable energy share in the total final energy consumption",
        "agency": "SPC",
        "dataflow": "DF_SDG",
        "version": "3.0",
        "key": "A.EG_FEC_RNEW.._T._T._T._T._T._T._Z._T",
        "source_url": "https://stats.pacificdata.org/vis?fs[0]=Development%20indicators,0%7CSustainable%20Development%20Goals%23SDG%23&pg=0&fc=Development%20indicators&bp=true&snb=18&df[ds]=ds%3ASPC2&df[id]=DF_SDG&df[ag]=SPC&df[vs]=3.0&dq=A.EG_FEC_RNEW.._T._T._T._T._T._T._Z._T&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "safely_managed_drinking_water_services",
        "title": "Proportion of population using safely managed drinking water services",
        "agency": "SPC",
        "dataflow": "DF_SDG_06",
        "version": "3.0",
        "key": "A.SH_H2O_SAFE...._T.....",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=ds%3ASPC2&df[id]=DF_SDG_06&df[ag]=SPC&df[vs]=3.0&dq=A.SH_H2O_SAFE...._T.....&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "power_generation",
        "title": "Power generation",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.POWER_GEN.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.POWER_GEN.&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "power_generation_disaggregated",
        "title": "Power generation - disaggregated",
        "agency": "SPC",
        "dataflow": "DF_POWER_GEN",
        "version": "1.0",
        "key": "A...",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_POWER_GEN&df[ag]=SPC&df[vs]=1.0&av=true&dq=A...&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "meteorological_monitoring_network",
        "title": "Meteorological monitoring network",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.METEO_MONITOR_NET.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.METEO_MONITOR_NET.&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "meteorological_monitoring_network_disaggregated",
        "title": "Meteorological monitoring network - disaggregated",
        "agency": "SPC",
        "dataflow": "DF_METEO_MONITOR_NET",
        "version": "1.0",
        "key": "A..",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_METEO_MONITOR_NET&df[ag]=SPC&df[vs]=1.0&av=true&dq=A..&pd=,&to[TIME_PERIOD]=false",
    },
    {
        "slug": "fisheries_management_measures_and_arrangements",
        "title": "Fisheries management measures in place and multilateral and bilateral fisheries management arrangements",
        "agency": "SPC",
        "dataflow": "DF_CLIMATE_CHANGE",
        "version": "1.0",
        "key": "A.FISH_MNGT_MULT_BILAT_ARGMT.",
        "source_url": "https://stats.pacificdata.org/vis?lc=en&df[ds]=SPC2&df[id]=DF_CLIMATE_CHANGE&df[ag]=SPC&df[vs]=1.0&av=true&dq=A.FISH_MNGT_MULT_BILAT_ARGMT.&pd=,&to[TIME_PERIOD]=false",
    },
]


COASTLINE_DATASET = {
    "slug": "coastline",
    "title": "Coastline",
    "source_url": "https://pacificdata.org/data/dataset/landsat-coastlines",
    "stac_collection_url": "https://stac.prod.digitalearthpacific.io/collections/dep_ls_coastlines",
    "files": [
        {
            "filename": "dep_ls_coastlines_0-7-0-55.pmtiles",
            "url": "https://s3.us-west-2.amazonaws.com/dep-public-data/dep_ls_coastlines/dep_ls_coastlines_0-7-0-55.pmtiles",
            "title": "Landsat Coastlines PMTiles",
        },
        {
            "filename": "dep_ls_coastlines_0-7-0-55.gpkg",
            "url": "https://s3.us-west-2.amazonaws.com/dep-public-data/dep_ls_coastlines/dep_ls_coastlines_0-7-0-55.gpkg",
            "title": "Landsat Coastlines Geopackage",
        },
        {
            "filename": "wmts.xml",
            "url": "https://tileserver.prod.digitalearthpacific.io/styles/coastlines/wmts.xml",
            "title": "WMTS service capabilities",
        },
    ],
}


def dotstat_url(dataset: dict[str, str]) -> str:
    flow = ",".join([dataset["agency"], dataset["dataflow"], dataset["version"]])
    key = quote(dataset["key"], safe=".+_")
    return f"{DOTSTAT_API}/{flow}/{key}?dimensionAtObservation=AllDimensions&format=csv"


def run_curl(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "curl",
        "-L",
        "--fail",
        "--silent",
        "--show-error",
        "--retry",
        "4",
        "--retry-delay",
        "2",
        "--continue-at",
        "-",
        "--user-agent",
        USER_AGENT,
        "--output",
        str(target),
        url,
    ]
    subprocess.run(cmd, check=True)


def download_text(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "en"})
    with urlopen(request, timeout=120) as response:
        content = response.read()
    target.write_bytes(content)


def download_file(url: str, target: Path) -> None:
    if target.exists() and target.stat().st_size > 0:
        print(f"skip existing {target.relative_to(ROOT)}")
        return
    print(f"download {target.relative_to(ROOT)}")
    if shutil.which("curl"):
        run_curl(url, target)
    else:
        download_text(url, target)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


def file_size(path: Path) -> int:
    return path.stat().st_size if path.exists() else 0


def write_readme() -> None:
    readme = DATA_DIR / "README.md"
    lines = [
        "# Pacific Dataviz Challenge 2026 Data",
        "",
        "Official datasets downloaded from the Pacific Dataviz Challenge 2026 list.",
        "",
        "- Competition page: https://pacificdatavizchallenge.org/",
        "- .Stat API endpoint: https://stats-nsi-stable.pacificdata.org",
        "- Coastline catalogue: https://pacificdata.org/data/dataset/landsat-coastlines",
        "",
        "Each subfolder corresponds to one official list entry. Tabular datasets contain `data.csv` plus `metadata.json`. The coastline dataset contains STAC metadata and geospatial resources.",
        "",
        "Note: the coastline `.gpkg` and `.pmtiles` files are large. Use Git LFS or keep `data/` untracked if this repository will be pushed to GitHub.",
        "",
    ]
    readme.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    downloaded_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest_rows: list[dict[str, str | int]] = []

    for dataset in DOTSTAT_DATASETS:
        dataset_dir = DATA_DIR / dataset["slug"]
        dataset_dir.mkdir(parents=True, exist_ok=True)
        api_url = dotstat_url(dataset)
        data_file = dataset_dir / "data.csv"
        download_file(api_url, data_file)

        metadata = {
            "api_url": api_url,
            "dataflow": dataset["dataflow"],
            "downloaded_at_utc": downloaded_at,
            "files": [{"path": "data.csv", "size_bytes": file_size(data_file)}],
            "key": dataset["key"],
            "source_url": dataset["source_url"],
            "title": dataset["title"],
            "type": "dotstat_csv",
        }
        write_json(dataset_dir / "metadata.json", metadata)

        manifest_rows.append(
            {
                "slug": dataset["slug"],
                "title": dataset["title"],
                "type": "dotstat_csv",
                "local_files": "data.csv; metadata.json",
                "size_bytes": file_size(data_file),
                "rows": count_csv_rows(data_file),
                "source_url": dataset["source_url"],
                "api_url": api_url,
            }
        )

    coastline_dir = DATA_DIR / COASTLINE_DATASET["slug"]
    coastline_dir.mkdir(parents=True, exist_ok=True)
    stac_file = coastline_dir / "collection.json"
    download_file(COASTLINE_DATASET["stac_collection_url"], stac_file)

    coastline_files = [{"path": "collection.json", "size_bytes": file_size(stac_file)}]
    for item in COASTLINE_DATASET["files"]:
        target = coastline_dir / item["filename"]
        download_file(item["url"], target)
        coastline_files.append(
            {
                "path": item["filename"],
                "size_bytes": file_size(target),
                "title": item["title"],
                "url": item["url"],
            }
        )

    write_json(
        coastline_dir / "metadata.json",
        {
            "downloaded_at_utc": downloaded_at,
            "files": coastline_files,
            "source_url": COASTLINE_DATASET["source_url"],
            "stac_collection_url": COASTLINE_DATASET["stac_collection_url"],
            "title": COASTLINE_DATASET["title"],
            "type": "stac_geospatial",
        },
    )
    manifest_rows.append(
        {
            "slug": COASTLINE_DATASET["slug"],
            "title": COASTLINE_DATASET["title"],
            "type": "stac_geospatial",
            "local_files": "; ".join(file["path"] for file in coastline_files) + "; metadata.json",
            "size_bytes": sum(int(file["size_bytes"]) for file in coastline_files),
            "rows": "",
            "source_url": COASTLINE_DATASET["source_url"],
            "api_url": COASTLINE_DATASET["stac_collection_url"],
        }
    )

    manifest_path = DATA_DIR / "manifest.csv"
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "slug",
                "title",
                "type",
                "local_files",
                "size_bytes",
                "rows",
                "source_url",
                "api_url",
            ],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    write_readme()
    print(f"wrote {manifest_path.relative_to(ROOT)}")
    print(f"datasets: {len(manifest_rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
