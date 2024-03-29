/**
 * Creates a pseudo-random value generator. The seed must be an integer.
 *
 * Uses an optimized version of the Park-Miller PRNG.
 * http://www.firstpr.com.au/dsp/rand31/
 */
function Random(seed) {
  this._seed = seed % 2147483647;
  if (this._seed <= 0) this._seed += 2147483646;
}

/**
 * Returns a pseudo-random value between 1 and 2^32 - 2.
 */
Random.prototype.next = function() {
  return (this._seed = (this._seed * 16807) % 2147483647);
};

/**
 * Returns a pseudo-random floating point number in range [0, 1).
 */
Random.prototype.nextFloat = function(opt_minOrMax, opt_max) {
  // We know that result of next() will be 1 to 2147483646 (inclusive).
  return (this.next() - 1) / 2147483646;
};

Random.prototype.nextByte = function(opt_minOrMax, opt_max) {
  // We know that result of next() will be 1 to 2147483646 (inclusive).
  return Math.floor((256 * (this.next() - 1)) / 2147483646);
};

function color(context) {
  var index = context.dataIndex;
  let r = new Random(index);
  r.nextByte();
  c =
    "rgba(" + r.nextByte() + ", " + r.nextByte() + ", " + r.nextByte() + ", 1)";
  return c;
}

const SHOW_ALL = 'Show all players';
const HIDE_ALL = 'Hide all players';
const SHOW_LAST = 'Show players in last match';

/**
 *  Sets label to "Show all" or "Hide all" depending on state
 */
function updateToggleLabels(showAll, showLast) {
  document.getElementById('toggle-all').innerHTML = showAll ? SHOW_ALL : HIDE_ALL;
  document.getElementById('toggle-last').innerHTML = showLast ? SHOW_LAST : SHOW_ALL;

  // Don't show the "Show last match" button with SHOW_ALL label if the show all
  // button will show the same thing
  document.getElementById('toggle-last').style.display = document.getElementById('toggle-all').innerHTML == document.getElementById('toggle-last').innerHTML ? 'none' : 'inline';
}

function isAnyLineHidden(chart) {
  let anyIsHidden = false;

  chart.data.datasets.forEach(function (ds, index) {
    if (chart.getDatasetMeta(index).hidden)
      anyIsHidden = true;
  });
  return anyIsHidden;
}

function setupChart(ctx, gameData) {
  const DEFAULT_LINE_WIDTH = 3;

  let chart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: Object.keys(gameData.rating_history)
        // Sort datasets to make legends come in alphabetical order
        .sort()
        .map(function(name, index) {
          let history = gameData.rating_history[name];
          let theColor = color({ dataIndex: index });

          return {
            lineTension: 0.2,
            fill: false,
            backgroundColor: theColor,
            borderColor: theColor,
            borderWidth: DEFAULT_LINE_WIDTH,
            label: name,
            data: Object.keys(history).map(function(matchNumber) {
              return { x: matchNumber, y: Math.round(history[matchNumber]) };
           })
          };
        }
      )
    },

    options: {
      // Use monotone because it looks a little better
      // See https://www.chartjs.org/docs/latest/charts/line.html#cubicinterpolationmode
      cubicInterpolationMode: "monotone",
      elements: {
        point: {
          // Make the points a smaller than default and bigger when hovering
          radius: 2,
          hoverRadius: 10
        }
      },
      legend: {
        display: true,
        position: "bottom"
      },
      tooltips: {
        mode: "nearest",
        intersect: false
      },
      plugins: {
        legend: {
          title: {
            display: true,
            padding: 10,
            text: "Hover name to highlight line",
          },
          position: "bottom",
          // Make current line stand out when hovering over its legend
          onHover: (evt, legendItem) => {
            if (chart.isDatasetVisible(legendItem.datasetIndex)) {
              let datasets = evt.chart.data.datasets;
              for (let i = 0; i < datasets.length; i++) {
                datasets[i].borderWidth = 1;
              }
              let data = datasets[legendItem.datasetIndex];
              data.borderWidth = DEFAULT_LINE_WIDTH * 3;
              chart.update();
            }
          },
          // Reset lines when leaving legend
          onLeave: (evt) => {
            let datasets = evt.chart.data.datasets;
            for (let i = 0; i < datasets.length; i++) {
              datasets[i].borderWidth = DEFAULT_LINE_WIDTH;
            }
            chart.update();
          },
          onClick: (evt, legendItem, legend) => {
            // Default legend onClick from https://www.chartjs.org/docs/latest/configuration/legend.html#custom-on-click-actions
            const index = legendItem.datasetIndex;
            const ci = legend.chart;
            if (ci.isDatasetVisible(index)) {
                ci.hide(index);
                legendItem.hidden = true;
            } else {
                ci.show(index);
                legendItem.hidden = false;
            }
            // End default legend onClick

            // Make sure the toggle all label is correct
            updateToggleLabels(isAnyLineHidden(chart), true);
          }
        }
      },
      scales: {
        x: {
          type: "linear",
        }
      },
      maintainAspectRatio: false
    }
  });

  /**
   * Toggles all lines on/off
   * If at least one line is hidden, show all lines
   * If all lines are shown, hide all lines
   */
  let showHideAllLines = function(event) {
    let anyIsHidden = isAnyLineHidden(chart);

    chart.data.datasets.forEach(function(ds, index) {
      chart.getDatasetMeta(index).hidden = !anyIsHidden;
    });
    chart.update();

    updateToggleLabels(isAnyLineHidden(chart), true);

    event.preventDefault();
  }

  /**
   * Toggles showing only lines from the last match on/off
   * If the last match is shown, show all lines
   * Otherwise, show the last match
   */
  let showHideLast = function(event) {
    // For every player find the index of theirs last match
    let lastMatchIndex = Object.keys(gameData.rating_history).reduce(function(acc, name) {
      let history = gameData.rating_history[name];
      let lastMatch = Object.keys(history).reduce(function(acc, matchNumber) {
        return Math.max(acc, matchNumber);
      }, 0);
      return Math.max(acc, lastMatch);
    }, 0);

    // Find all players who played in the last match
    let playersToShow = Object.keys(gameData.rating_history).filter(function(name) {
      let history = gameData.rating_history[name];
      return Object.keys(history).includes(lastMatchIndex.toString());
    });

    // Check if these players are exactly the ones that are shown
    let matchesPlayersToShow = true;
    chart.data.datasets.forEach(function(ds, index) {
      let name = ds.label;
      let isShown = !chart.getDatasetMeta(index).hidden;

      if (playersToShow.includes(name) != isShown) {
        matchesPlayersToShow = false;
      }
    });

    // If the players are exactly the ones that are shown, show all lines
    // Otherwise, show only the players in the last match
    chart.data.datasets.forEach(function(ds, index) {
      let name = ds.label;
      chart.getDatasetMeta(index).hidden = matchesPlayersToShow ? false : !playersToShow.includes(name);
    });

    chart.update();

    // matchPlayersToShow tells if all players in the last match were shown *before* our update and
    // is now the opposite of that
    updateToggleLabels(isAnyLineHidden(chart), matchesPlayersToShow);

    event.preventDefault();
  }

  updateToggleLabels(false, true);
  document.getElementById('toggle-all').addEventListener('click', showHideAllLines);
  document.getElementById('toggle-last').addEventListener('click', showHideLast);

  return chart;
}

$(function() {
  var firstTime = true;

  $('#toggle-chart').click(function() {
      if (firstTime) {
          let ctx = $('#chart').get(0).getContext('2d');

          fetch('game.json')
              .then(function(response) {
                  return response.json();
              })
              .then(function(gameData) {
                  firstTime = false;
                  setupChart(ctx, gameData);
                  $('#chart-container').fadeToggle();
                })
              .catch(function(error) {
                console.error('Could not load game data', error);
              });
      } else {
          $('#chart-container').fadeToggle();
      }
  });
});
