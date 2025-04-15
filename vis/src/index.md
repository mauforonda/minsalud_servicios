<link rel="stylesheet" href="style.css">

```js
// Some general definitions
const colors = {
    selection: "#6b9778",
    selection_muted: "#6b977826",
    selection_glow: "#6aae65",
    stroke: "#67676c",
};
const github =
    "https://raw.githubusercontent.com/mauforonda/minsalud_servicios/main";
const defaultService = {
    file: "clean/2024/recien-nacidos-en-servicio-y-domicilio/nacidos-vivos-atendidos-por-partera.csv",
    service: "nacidos vivos atendidos por partera",
    service_group: "recien nacidos en servicio y domicilio",
    year: 2024,
};
const suggestions = {
    consulta: "consulta",
    internaciones: "internaciones",
    cirugia: "cirugía",
    "interrupcion legal del embarazo": "interrupcion legal del embarazo",
    anticoncepcion: "anticoncepcion",
    vacunaciones: "vacunaciones",
    partos: "partos",
    nacidos: "nacidos",
    "atencion odontologica": "odontología",
    comunidad: "actividades con la comunidad",
    micronutrientes: "micronutrientes",
    telesalud: "telesalud",
    dengue: "dengue",
    malaria: "malaria",
    vih: "vih",
    chagas: "chagas",
    rabia: "rabia",
    its: "its",
    "salud mental": "salud mental",
};
```

```js
// Load index
const indexCSV = await d3
    .csv(`${github}/indexes/clean.csv`, d3.autoType)
    .then((data) =>
        data
            .filter((d) => d.values > 0)
            .map((d) => {
                return {
                    ...d,
                    ...{
                        x: d.year + (Math.random() - 0.5) * 0.4,
                    },
                };
            })
    );
```

```js
// Index suggestions
const suggestionButtons = Inputs.radio(Object.keys(suggestions), {
    format: (d) => suggestions[d],
});
const suggestionSelected = Generators.input(suggestionButtons);
```

```js
// Index search
const indexSearch = Inputs.search(indexCSV, {
    query: suggestionSelected,
    columns: ["service_group", "service"],
    required: false,
    format: (d) => "",
    placeholder: "busca",
});
const indexSearchQuery = Generators.input(indexSearch);
```

```js
// Index plot
const plotIndex = (index) => {
    const dotOps = {
        x: "x",
        y: "values",
        stroke: null,
    };
    return Plot.plot({
        width: width,
        height: 350,
        marginBottom: 30,
        marginTop: 45,
        y: {
            axis: null,
            type: "symlog",
        },
        x: {
            tickSize: 0,
            label: null,
            axis: "top",
            tickPadding: 15,
            tickFormat: (d) => d3.format(".0f")(d),
        },
        style: {
            color: colors.stroke,
        },
        marks: [
            Plot.dot(index, {
                ...dotOps,
                r: 1,
                stroke: null,
                fill: true,
                fillOpacity: (d) => (indexSearchQuery.length > 0 ? 0.1 : 0.5),
            }),
            Plot.dot(indexSearchQuery, {
                ...dotOps,
                r: 1.5,
                stroke: null,
                fill: colors.selection,
                fillOpacity: 1,
            }),
            Plot.dot(
                indexSearchQuery.length > 0 ? indexSearchQuery : index,
                Plot.pointer({
                    ...dotOps,
                    r: 10,
                    stroke: null,
                    fill: colors.selection,
                    fillOpacity: 0.2,
                })
            ),
            Plot.dot(
                indexSearchQuery.length > 0 ? indexSearchQuery : index,
                Plot.pointer({
                    ...dotOps,
                    r: 2,
                    stroke: null,
                    fill: colors.selection_glow,
                    fillOpacity: 0.9,
                })
            ),
        ],
    });
};
const indexPlot = plotIndex(indexCSV);
const hoveredService = Generators.input(indexPlot);
```

```js
// A placeholder input for the service to download
const serviceInput = Inputs.input(defaultService);
const service = Generators.input(serviceInput);
```

```js
// The download button
const set = (input, value) => {
    input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
};

const makeServiceButton = (s, clickTarget) => {
    return htl.html`
    <div class="serviceButton ${
        clickTarget ? "target" : ""
    }" title="Descarga y consulta">
        <div>
            <span class="buttonService">${s.service}</span>
            <span class="buttonYear">en ${s.year}</span>
        </div>
        <div>
            <span class="buttonGroup">${s.service_group}</span>
        </div>
    </div>`;
};

const serviceButton = htl.html`${
    hoveredService
        ? makeServiceButton(hoveredService, true)
        : service
        ? makeServiceButton(service, false)
        : "..."
}`;

serviceButton.onclick = () => {
    set(serviceInput, hoveredService);
};
```

```js
// Download service data
const serviceCSV = (await service.service)
    ? d3.csv(`${github}/${service.file}`, d3.autoType)
    : null;
```

```js
const populations = Object.entries(
    serviceCSV.reduce((acc, item) => {
        const { population, value } = item;
        acc[population] = (acc[population] || 0) + value;
        return acc;
    }, {})
).map(([population, value]) => ({ population, value }));
```

```js
// Population input
const defaultPopulation = populations
    .filter((population) =>
        population.population.toLowerCase().includes("total")
    )
    .slice(-1)[0];
```

```js
const population = selectedPopulation ? selectedPopulation : defaultPopulation;
```

```js
const plotPopulationBars = (populations) => {
    const top = Math.max(...populations.map((p) => p.value)) * 1.2;
    const barParams = {
        x: "value",
        y: "population",
        insetTop: 30,
        r: 2,
    };

    const textParams = {
        text: (d) => d.population.toLowerCase(),
        x: 0,
        y: "population",
        stroke: "var(theme-background)",
        fill: colors.stroke,
        fontFamily: "Inter",
        fontSize: 12,
        dy: -6,
        textAnchor: "start",
    };

    return Plot.plot({
        width: 450,
        height: populations.length * 50,
        className: "populationBars",
        x: {
            axis: null,
            domain: [0, top],
        },
        y: {
            axis: null,
        },
        style: {
            color: colors.stroke,
        },
        marks: [
            Plot.barX(populations, {
                ...barParams,
                fill: colors.stroke,
                fillOpacity: (d) =>
                    d.population == defaultPopulation.population ? 0.5 : 0.2,
                sort: {
                    y: "-x",
                },
            }),
            Plot.barX(
                populations,
                Plot.pointerY({
                    ...barParams,
                    fill: colors.selection,
                })
            ),
            Plot.text(populations, {
                ...textParams,
                fillOpacity: (d) =>
                    d.population == defaultPopulation.population ? 0.9 : 0.7,
            }),
            Plot.text(populations, {
                x: "value",
                y: "population",
                text: "value",
                textAnchor: "start",
                lineAnchor: "top",
                dy: 11,
                dx: 5,
                fillOpacity: (d) =>
                    d.population == defaultPopulation.population ? 0.9 : 0.7,
            }),
            Plot.text(
                populations,
                Plot.pointerY({
                    ...textParams,
                    fillOpacity: 0.9,
                })
            ),
        ],
    });
};
const populationBars = plotPopulationBars(populations);
const selectedPopulation = Generators.input(populationBars);
```

```js
// Load municipality limits
const topo = await FileAttachment("bolivia.json").json();
const bolivia = topojson.feature(topo, topo.objects.data);
```

```js
const processGeo = (data) => {
    const municipalityTotals = data.reduce((acc, item) => {
        const { municipality_id, municipality, population, value } = item;

        if (!acc[municipality_id]) {
            acc[municipality_id] = {};
        }
        acc[municipality_id][population] =
            (acc[municipality_id][population] || 0) + value;
        acc[municipality_id].municipality = municipality;

        return acc;
    }, {});

    const features = [];
    bolivia.features.forEach((f) => {
        if (municipalityTotals[f.id]) {
            features.push({
                ...f,
                properties: {
                    ...municipalityTotals[f.id],
                    centroid: d3.geoCentroid(f),
                },
            });
        }
    });
    return {
        type: "FeatureCollection",
        features: features,
    };
};
```

```js
const serviceGeo = processGeo(serviceCSV);
```

```js
const makeMap = (population) => {
    const textParams = {
        px: (d) => d.properties.centroid[0],
        py: (d) => d.properties.centroid[1],
        dx: 0,
        fill: colors.stroke,
        frameAnchor: "top-right",
        textAnchor: "end",
    };
    const max = Math.max(
        ...serviceGeo.features.map((i) => i.properties[population])
    );
    const w = width > 1100 ? width * 0.3 - 0 : width;
    const mapPlot = Plot.plot({
        height: w,
        width: w,
        marginLeft: 30,
        marginRight: 30,
        marginTop: 30,
        marginBottom: 5,
        color: {
            range: [colors.selection_muted, colors.selection],
            // domain: [0, 1e3]
        },
        projection: {
            type: "mercator",
            domain: bolivia,
        },
        marks: [
            Plot.geo(bolivia, {
                fill: colors.stroke,
                fillOpacity: 0.15,
            }),
            Plot.geo(serviceGeo, {
                fill: "var(--theme-background-alt)",
            }),
            Plot.geo(serviceGeo, {
                fill: (d) => d.properties[population],
                stroke: colors.stroke,
                strokeOpacity: 0.2,
            }),
            Plot.geo(
                serviceGeo.features,
                Plot.pointer(
                    Plot.centroid({
                        fill: (d) => d.properties[population],
                        stroke: "var(--theme-foreground)",
                        strokeWidth: 1,
                    })
                )
            ),
            Plot.text(
                serviceGeo.features,
                Plot.pointer({
                    ...textParams,
                    dy: w / 40,
                    lineAnchor: "bottom",
                    stroke: "var(theme-background)",
                    fill: colors.selection,
                    fontFamily: "serif",
                    fontStyle: "italic",
                    fontWeight: "bold",
                    fontSize: w / 15,
                    text: (d) =>
                        `${d3.format(",.0f")(d.properties[population])}`,
                })
            ),
            Plot.text(
                serviceGeo.features,
                Plot.pointer({
                    ...textParams,
                    text: (d) => `en ${d.properties.municipality}`,
                    dy: w / 40 + 10,
                    lineAnchor: "top",
                    fontSize: w / 30,
                    fontFamily: "serif",
                    fontStyle: "italic",
                })
            ),
        ],
    });
    const mapLegend = Plot.legend({
        color: {
            domain: [0, max],
            range: [colors.selection_muted, colors.selection],
            type: "linear",
            ticks: 5,
        },
        className: "mapLegend",
        width: w,
        height: 50,
        marginTop: 20,
        marginLeft: 50,
        marginRight: 50,
    });
    return htl.html`<div class="">${mapPlot}${mapLegend}</div>`;
};
```

```js
const mapa = makeMap(population.population);
```

```js
const processTime = (data) => {
    return data.reduce((acc, item) => {
        const { population, month, value } = item;

        if (!acc[population]) {
            acc[population] = Array(12)
                .fill()
                .map((_, i) => ({ month: i + 1, value: 0 }));
        }

        acc[population][month - 1].value += value;

        return acc;
    }, {});
};
```

```js
const serviceTime = processTime(serviceCSV);
```

```js
const makeTimeline = (population) => {
    const top = Math.max(...population.map((i) => i.value)) * 1.1;
    const w = width > 1100 ? width * 0.5 - 40 : width;
    const h = width > 1100 ? width * 0.2 + 20 : width * 0.55;
    const maxRadius = w / 30;
    const marginTop = w > 660 ? w / 12 : 50;
    const smallFont = w > 660 ? w / 80 : 11;
    const largeFont = w > 660 ? w / 35 : 15;
    const monthFormat = {
        1: "enero",
        2: "febrero",
        3: "marzo",
        4: "abril",
        5: "mayo",
        6: "junio",
        7: "julio",
        8: "agosto",
        9: "septiembre",
        10: "octubre",
        11: "noviembre",
        12: "diciembre",
    };
    const lineParams = {
        x: "month",
        y: "value",
        curve: "basis",
    };
    const gridParams = {
        stroke: colors.stroke,
        strokeDasharray: "1 1",
        strokeWidth: 0.5,
        strokeOpacity: 0.5,
    };
    const textParams = {
        x: "month",
        y: top,
        stroke: "var(theme-background)",
        fontFamily: "serif",
        fontStyle: "italic",
    };
    const tickParams = {
        y: (d) => d,
        text: (d) => d3.format(",.0f")(d),
        stroke: "var(theme-background)",
        fill: colors.stroke,
        fontFamily: "serif",
        fontStyle: "italic",
        frameAnchor: "right",
        textAnchor: "end",
        fontSize: smallFont,
        fillOpacity: 0.5,
        dx: -10,
    };
    return Plot.plot({
        height: h,
        width: w,
        marginLeft: 30,
        marginRight: 30,
        marginTop: marginTop,
        marginBottom: 5,
        x: {
            axis: null,
            domain: [1, 12],
        },
        y: {
            domain: [0, top],
            axis: null,
        },
        style: {
            color: colors.stroke,
        },
        marks: [
            Plot.gridY({
                ...gridParams,
            }),
            Plot.gridX({
                ...gridParams,
            }),
            Plot.areaY(population, {
                ...lineParams,
                fill: colors.selection_muted,
            }),
            Plot.line(population, {
                ...lineParams,
                stroke: colors.selection,
                strokeWidth: 4,
                strokeOpacity: 0.7,
            }),
            Plot.dot(population, {
                ...lineParams,
                fill: colors.selection,
                fillOpacity: 0.4,
                stroke: null,
                r: 5,
            }),
            Plot.ruleX([1, 12], {
                ...gridParams,
            }),
            Plot.ruleY([0, top], {
                ...gridParams,
            }),
            Plot.dot(
                population,
                Plot.pointerX({
                    ...lineParams,
                    fill: colors.selection,
                    fillOpacity: 0.2,
                    stroke: null,
                    r: 15,
                })
            ),
            Plot.dot(
                population,
                Plot.pointerX({
                    stroke: null,
                    fill: colors.selection,
                    ...lineParams,
                    r: 5,
                })
            ),
            Plot.text(
                population,
                Plot.pointerX({
                    ...textParams,
                    filter: (d) => d.month < 11,
                    text: "value",
                    dy: -30,
                    fill: colors.selection,
                    fontWeight: "bold",
                    fontSize: largeFont,
                    lineAnchor: "bottom",
                    textAnchor: "start",
                    maxRadius: maxRadius,
                })
            ),
            Plot.text(
                population,
                Plot.pointerX({
                    ...textParams,
                    filter: (d) => d.month >= 11,
                    text: "value",
                    dy: -30,
                    fill: colors.selection,
                    fontWeight: "bold",
                    fontSize: largeFont,
                    lineAnchor: "bottom",
                    textAnchor: "end",
                    maxRadius: maxRadius,
                })
            ),
            Plot.text(
                population,
                Plot.pointerX({
                    ...textParams,
                    filter: (d) => d.month < 11,
                    text: (d) => `en ${monthFormat[d.month]}`,
                    dy: -20,
                    fill: colors.stroke,
                    lineAnchor: "top",
                    fontSize: smallFont,
                    textAnchor: "start",
                    maxRadius: maxRadius,
                })
            ),
            Plot.text(
                population,
                Plot.pointerX({
                    ...textParams,
                    filter: (d) => d.month >= 11,
                    text: (d) => `en ${monthFormat[d.month]}`,
                    dy: -20,
                    fill: colors.stroke,
                    lineAnchor: "top",
                    fontSize: smallFont,
                    textAnchor: "end",
                    maxRadius: maxRadius,
                })
            ),
            Plot.text([0], {
                ...tickParams,
                lineAnchor: "bottom",
                dy: -10,
            }),
            Plot.text([top], {
                ...tickParams,
                lineAnchor: "top",
                dy: 10,
            }),
        ],
    });
};
```

```js
const timeline = makeTimeline(serviceTime[population.population]);
```

```js
function download(value, name = "untitled", label = "Save", title="en formato CSV") {
    const a = document.createElement("a");
    const b = a.appendChild(document.createElement("button"));
    b.textContent = label;
    a.title = title;
    a.download = name;

    async function reset() {
        await new Promise(requestAnimationFrame);
        URL.revokeObjectURL(a.href);
        a.removeAttribute("href");
        b.textContent = label;
        b.disabled = false;
    }

    a.onclick = async (event) => {
        b.disabled = true;
        if (a.href) return reset();
        b.textContent = "Saving…";
        try {
            const object = await (typeof value === "function"
                ? value()
                : value);
            b.textContent = "Download";
            a.href = URL.createObjectURL(object);
        } catch (ignore) {
            b.textContent = label;
        }
        if (event.eventPhase) return reset();
        b.disabled = false;
    };

    return a;
}

const button = (data, filename="data.csv", label="Save") => {
    const downloadData = new Blob([d3.csvFormat(data)], { type: "text/csv" });
    const button = download(
        downloadData,
        filename,
        label
    );
    return button
};

const downloadButton = button(serviceCSV, service.file, `${service.service} en ${service.year}`);
const downloadAll = htl.html`<a href="https://github.com/mauforonda/minsalud_servicios/releases/latest" target="_blank" title="en formato parquet">
todos los datos
</a>`;
```

```js
const sprout = htl.svg`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${colors.selection}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-sprout-icon lucide-sprout"><path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/></svg>`
```

<div class="main">
    <div class="topHeader">
        <div class="title">
            Servicios de Salud en Bolivia
        </div>
        <div class="subtitle">
            Estadísticas del Formulario 301a de Producción de Servicios del Ministerio de Salud de Bolivia entre 2005 y 2024
        </div>
    </div>
    <div class="section">busca</div>
    <div class="index">
        <div class="search">
            ${indexSearch}
            <div class="suggestions">
                ${suggestionButtons}
            </div>
        </div>
        <div class="focus indexPlot">
            <div class="hint">datos disponibles</div>
            ${indexPlot}
        </div>
    </div>
    <div class="section">consulta</div>
    <div class="service">
        <div class="header">
            ${serviceButton}
        </div>
        <div class="plots">
            <div class="plotSection">
                <div class="populations">
                    <div class="hint">categorías disponibles</div>
                    ${populationBars}
                </div>
                <div class="timeline">
                    <div class="hint">en meses</div>
                    ${timeline}
                </div>
            </div>
            <div class="plotSection">
                <div class="map">
                    <div class="hint">en municipios</div>
                    ${mapa}
                </div>
            </div>
        </div>
        <div class="plots">
        </div>
    </div>
    <div class="section">descarga</div>
    <div class="download">
        ${downloadButton}
        ${downloadAll}
    </div>
    <div class="section">créditos</div>
    <div class="credits">
        Datos publicados en los <a href="https://estadisticas.minsalud.gob.bo/" target="_blank">reportes estadísticos del formulario 301a</a> del Ministerio de Salud y Deportes de Bolivia. <a href="https://github.com/mauforonda/minsalud_servicios/" target="_blank">Código para descargar, procesar y visualizar estos datos</a> por <a href="mailto:mauriforonda@gmail.com" target="_blank">Mauricio Foronda</a>. Errores ortográficos cortesía de trabajadores de salud.
    </div>
    <div class="footer">
        ${sprout}
    </div>
</div>
