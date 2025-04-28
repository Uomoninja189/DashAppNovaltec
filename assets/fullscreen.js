
window.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        addToModbar();
    }, 1000);
});

window.fetch = new Proxy(window.fetch, {
    apply(fetch, that, args) {
        const result = fetch.apply(that, args);
        result.then((response) => {
            if (args[0] === '/_dash-update-component') {
                setTimeout(function () {
                    addToModbar();
                }, 1000);
            }
        });
        return result;
    }
});

function addToModbar() {
    const modeBars = document.querySelectorAll(".modebar-container");
    for (let i = 0; i < modeBars.length; i++) {
        const modeBarGroups = modeBars[i].querySelectorAll(".modebar-group");
        const modeBarBtns = modeBarGroups[modeBarGroups.length - 1].querySelectorAll(".modebar-btn");

        if (modeBarBtns[modeBarBtns.length - 1].getAttribute('data-title') !== 'Fullscreen') {
            const aTag = document.createElement('a');
            aTag.className = "modebar-btn";
            aTag.setAttribute("rel", "tooltip");
            aTag.setAttribute("data-title", "Fullscreen");
            aTag.setAttribute("style", "color:gray");
            aTag.setAttribute("onClick", "fullscreen(this);");
            const iTag = document.createElement('i');
            iTag.className = 'fa-solid fa-maximize';
            aTag.appendChild(iTag);
            modeBarGroups[modeBarGroups.length - 1].appendChild(aTag);
        }
    }
}


    function fullscreen(el) {
        const graphContainer = el.closest('.dash-graph'); 
        const plot = graphContainer.querySelector('.js-plotly-plot'); 
    
        // Dimensione font predefinita (puoi adattarla al tuo stile)
        const defaultFontSize = 12;
    
        function adjustFontSize(plot, isFullscreen = false) {
            if (!plot) return;
    
            if (!isFullscreen) {
                // Ripristina font normali
                Plotly.relayout(plot, {
                    'font.size': defaultFontSize,
                    'xaxis.title.font.size': defaultFontSize,
                    'yaxis.title.font.size': defaultFontSize,
                    'title.font': { size: defaultFontSize },
                    'hoverlabel.font.size': defaultFontSize
                });
                
            } else {
                // Calcola font proporzionato
                const width = plot.clientWidth;
                const height = plot.clientHeight;
                const fontSize = Math.max(Math.min(width / 40, height / 40), 10);
    
                Plotly.relayout(plot, {
                    'font.size': fontSize,
                    'xaxis.title.font.size': fontSize,
                    'yaxis.title.font.size': fontSize,
                    'title.font': { size: fontSize },
                    'hoverlabel.font.size': fontSize
                });
                
            }
        }
    
        function resizePlot(isFullscreen = false) {
            if (plot) {
                Plotly.Plots.resize(plot);
                adjustFontSize(plot, isFullscreen);
            }
        }
    
        // Entrata/uscita fullscreen
        function onFullScreenChange() {
            const isFullscreen = !!document.fullscreenElement;
            
            // Aspetta un attimo prima di ridisegnare
            setTimeout(() => {
                resizePlot(isFullscreen);
            }, 150);
        }
    
        // Rimuove vecchi listener, se presenti
        document.removeEventListener("fullscreenchange", onFullScreenChange);
        document.addEventListener("fullscreenchange", onFullScreenChange);
    
        // Entra/esce dal fullscreen
        if (document.fullscreenElement) {
            document.exitFullscreen?.();
        } else {
            graphContainer.requestFullscreen?.();
        }
    }
    