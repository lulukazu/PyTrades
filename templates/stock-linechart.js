
var StockLineChart = function(stockName, divID) {
    var divEl = document.getElementById(divID);
    var divW = divEl.offsetWidth, divH = divEl.offsetHeight;
    var svg = d3.select(divEl).append('svg')
        .attr("width", divW)
        .attr("height", divH);
    var me = this;

    var plotData = [];
    var animatedOn = true;

    var margin = {top: 20, right: 25, bottom: 40, left: 62},
        width = svg.attr('width') - margin.left - margin.right,
        height = svg.attr('height') - margin.top - margin.bottom;

    var x = d3.scaleTime().range([0, width]);
    var y = d3.scaleLinear().range([height, 0]);

    var valueline = d3.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.close); });

    var valueArea = d3.area()
        .x(function(d) { return x(d.date); })
        .y0(function(d) { return y(d.yMin); })
        .y1(function(d) { return y(d.yMax); });

    var content = svg
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    content.append('g')
        .classed('lines', true);

    // Hide content on top margin
    content.append('rect')
        .attr('fill', 'white')
        .attr('x', margin.left * -1)
        .attr('y', margin.top * -1)
        .attr('width', svg.attr('width'))
        .attr('height', margin.top);

    // Hide content on left margin
    content.append('rect')
        .attr('fill', 'white')
        .attr('x', margin.left * -1)
        .attr('y', 0)
        .attr('width', margin.left - 1)
        .attr('height', svg.attr('height'));

    // Hide content on bottom margin
    content.append('rect')
        .attr('fill', 'white')
        .attr('x', 0)
        .attr('y', height + 1)
        .attr('width', svg.attr('width'))
        .attr('height', margin.bottom);

    // Hide content on right margin
    content.append('rect')
        .attr('fill', 'white')
        .attr('x', width)
        .attr('y', 0)
        .attr('width', margin.right)
        .attr('height', height);

    content.append("text")
        .attr("x", width / 2 )
        .attr("y", 0)
        .style("text-anchor", "middle")
        .text(stockName + " Price")
        .style("font-size", "26px")
        .style("font-weight", "bold");

        //Create X axis label
    content.append("text")
        .attr("x", width / 2 )
        .attr("y",  height + margin.bottom)
        .style("text-anchor", "middle")
        .text("Date")
        .style("font-size", "16px")
        .style("font-weight", "bold");

        //Create Y axis label
    content.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0-margin.left)
        .attr("x",0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Price ($)")
        .style("font-size", "16px")
        .style("font-weight", "bold");;

    content.append("g")
        .attr("transform", "translate(0," + height + ")")
        .attr('class', 'x-axis')
        .call(d3.axisBottom(x).ticks(6));

    content.append("g")
        .attr('class', 'y-axis')
        .call(d3.axisLeft(y).ticks(8));

    resetScales();
    addBrush();
    addHover();

    function addBrush() {
        var brushStart = -1;

        var brush = content.append('rect')
            .classed('brush', true)
            .attr('y', 0)
            .attr('height', height);

        svg.on('mousedown', function() {
            brushStart = d3.event.offsetX - margin.left;
            d3.event.preventDefault();
        });
        svg.on('mousemove.brush', function() {
            if(brushStart !== -1) {
                var brushEnd = d3.event.offsetX - margin.left;
                var brushLeft = brushStart < brushEnd ? brushStart : brushEnd;
                var brushRight = brushStart < brushEnd ? brushEnd : brushStart;
                brush.attr('x', brushLeft)
                    .attr('width', brushRight - brushLeft);
                d3.event.preventDefault();
            }
        });
        svg.on('mouseup', function() {
            if(brushStart !== -1 && Math.abs(brushStart - (d3.event.offsetX - margin.left)) > 2) {
                var brushEnd = d3.event.offsetX - margin.left;
                var brushLeft = brushStart < brushEnd ? brushStart : brushEnd;
                var brushRight = brushStart < brushEnd ? brushEnd : brushStart;

                var domainBefore = x.domain().map(d => d.getTime());
                var domain = [x.invert(brushLeft), x.invert(brushRight)].map(d => d.getTime());

                brush.attr('width', 0);

                animateZoom(domainBefore, domain);
                d3.event.preventDefault();
            }
            brushStart = -1;
        });
        svg.on('dblclick', function() {
            var domainBefore = x.domain().map(d => d.getTime());
            var domain = getMaxXdomain();
            animateZoom(domainBefore, domain);
            d3.event.preventDefault();
        });

        function animateZoom(domainBefore, domain) {
            animatedOn = false;
            new Animation(600, function(t) {
                var currentDomain = [domainBefore[0] + (domain[0] - domainBefore[0]) * t,
                    domainBefore[1] + (domain[1] - domainBefore[1]) * t];
                x.domain(currentDomain);
                resetYScale();
                me.redraw();

                /*brush.attr('x', x(currentDomain[0]))
                    .attr('width', x(currentDomain[1]) - x(currentDomain[0]));*/

            }, function() {
                animatedOn = true;
            }).start();
        }
    }

    var hoverG = content.append('g')
        .classed('hovers', true);

    function addHover() {

        var hover = content.append('line')
            .attr('y1', 0)
            .attr('y2', height)
            .classed('hover-line', true);

        svg.on('mousemove.hover', function() {
            var currentX = x.invert(d3.event.offsetX - margin.left);
            hover.attr('x1', x(currentX))
                .attr('x2', x(currentX));

            for(let plot of plotData.filter(plot => plot.hover)) {
                if(plot.hover) {
                    var sortedLeft = plot.data.concat().filter(p => p.date < currentX)
                        .sort((a, b) => Math.abs(a.date - currentX) - Math.abs(b.date - currentX));
                    var sortedRight = plot.data.concat().filter(p => p.date > currentX)
                        .sort((a, b) => Math.abs(a.date - currentX) - Math.abs(b.date - currentX));
                    var closestTwo = [sortedLeft[0], sortedRight[0]];
                    if(closestTwo[0] === undefined || closestTwo[1] === undefined) return;

                    var distances = closestTwo.map(p => Math.abs(p.date - currentX));
                    var distanceRatio = distances[1] / (distances[0] + distances[1]);

                    if(plot.type === 'line') {
                        var currentY = closestTwo[0].close * distanceRatio + closestTwo[1].close * (1 - distanceRatio);
                        if(plot.hover.mark && plot.hover.mark === 'circle') {
                            plot.hover.markNode.select('circle')
                                .attr('cx', x(currentX))
                                .attr('cy', y(currentY));
                        }
                        if(plot.hover.showValue) {
                            var textValue = plot.hover.showValue(currentX, Math.round(currentY*100)/100);
                            plot.hover.showValueNode
                                .attr('x', x(currentX) > width * 3/4 ? x(currentX) - textValue.length * 10  : x(currentX) + 15)
                                .attr('y', y(currentY) + 5)
                                .text(textValue);
                            plot.hover.markNode.select('rect')
                                .attr('x', x(currentX) > width * 3/4 ? x(currentX) - textValue.length * 10 - 10 : x(currentX) + 10)
                                .attr('y', y(currentY) - 15)
                                .attr('width', textValue.length * 10);
                        }
                    } else if(plot.type === 'band') {
                        var currentYs = [closestTwo[0].yMin * distanceRatio + closestTwo[1].yMin * (1 - distanceRatio),
                            closestTwo[0].yMax * distanceRatio + closestTwo[1].yMax * (1 - distanceRatio)];
                        if(plot.hover.mark && plot.hover.mark === 'circle') {
                            plot.hover.markNode.select('circle:nth-child(1)')
                                .attr('cx', x(currentX))
                                .attr('cy', y(currentYs[0]));
                            plot.hover.markNode.select('circle:nth-child(2)')
                                .attr('cx', x(currentX))
                                .attr('cy', y(currentYs[1]));
                        }
                    }
                }
            }
        });
    }

    this.addLine = function(data, className, hover) {
        var obj = {
            type: 'line',
            className: className,
            data: data,
            hover: hover
        };
        if(obj.hover) {
            if(obj.hover.mark && obj.hover.mark === 'circle') {
                var markSize = obj.hover.markSize || 5;
                obj.hover.markNode = hoverG.append('g');
                obj.hover.markNode.append('circle')
                    .attr('r', markSize)
                    .style('pointer-events', 'none')
                    .classed(className + '-hover', true);
            }
            if(obj.hover.showValue) {
                obj.hover.markNode.append('rect')
                    .attr('fill', 'rgba(255,255,255,0.5)')
                    .attr('stroke', '#ccc')
                    .attr('rx', 10)
                    .attr('ry', 10)
                    .attr('height', 30);
                obj.hover.showValueNode = hoverG
                    .append('text')
                    .classed(className + '-hover', true);
            }
        }
        plotData.push(obj);
        resetScales();
        this.redraw();
    };

    this.addBand = function(data, className, hover) {
        var obj = {
            type: 'band',
            className: className,
            data: data,
            hover: hover
        };
        if(obj.hover) {
            if(obj.hover.mark && obj.hover.mark === 'circle') {
                var markSize = obj.hover.markSize || 5;
                obj.hover.markNode = hoverG.append('g');
                obj.hover.markNode.append('circle')
                    .attr('r', markSize)
                    .style('pointer-events', 'none')
                    .classed(className + '-hover', true);
                obj.hover.markNode.append('circle')
                    .attr('r', markSize)
                    .style('pointer-events', 'none')
                    .classed(className + '-hover', true);
            }
            if(obj.hover.showValue) {
                obj.hover.showValueNode = hoverG
                    .append('text')
                    .classed(className + '-hover', true);
            }
        }
        plotData.push(obj);
//        resetScales();
//        this.redraw();
    };

    this.addPoints = function(data, className, shape) {
        plotData.push({
            type: 'points',
            className: className,
            shape: shape,
            data: data
        });
        resetScales();
        this.redraw();
    };

    this.clearData = function() {
        plotData = [];
        resetScales();
        this.redraw();
    };

    function resetScales() {
        x.domain(getMaxXdomain());
        resetYScale();
    }

    function getMaxXdomain() {
        var xExtents = plotData.filter(p => p.type === 'line').map(plot => {
            return d3.extent(plot.data, function(d) { return d.date; });
        });

        return [Math.min.apply(null, xExtents.map(e => e[0])),
            Math.max.apply(null, xExtents.map(e => e[1]))];
    }

    function resetYScale() {
        var yExtents = plotData.filter(p => p.type === 'line' && p.data.filter(d => d.date >= x.domain()[0] && d.date <= x.domain()[1]).length
            ).map(plot => {
            var dataInX = plot.data.filter(d => d.date >= x.domain()[0] && d.date <= x.domain()[1]);
            return d3.extent(dataInX, function(d) { return d.close; });
        }).concat(plotData.filter(p => p.type === 'band' && p.data.filter(d => d.date >= x.domain()[0] && d.date <= x.domain()[1]).length).map(plot => {
            var dataInX = plot.data.filter(d => d.date >= x.domain()[0] && d.date <= x.domain()[1]);
            return d3.extent(dataInX, function(d) { return d.yMin; });
        })).concat(plotData.filter(p => p.type === 'band' && p.data.filter(d => d.date >= x.domain()[0] && d.date <= x.domain()[1]).length).map(plot => {
            var dataInX = plot.data.filter(d => d.date >= x.domain()[0] && d.date <= x.domain()[1]);
            return d3.extent(dataInX, function(d) { return d.yMax; });
        }));
        y.domain([Math.min.apply(null, yExtents.map(e => e[0])),
            Math.max.apply(null, yExtents.map(e => e[1]))]);
    }

    this.redraw = function() {
        var linesG = content.select('.lines').html('');

        for(let plot of plotData) {
            if(plot.type === 'line') {
                var path = linesG.append("path")
                    .data([plot.data])
                    .classed(plot.className, true)
                    .attr("d", valueline);
                /*var totalLength = path.node().getTotalLength();
                path
                  .attr("stroke-dasharray", totalLength + " " + totalLength)
                  .attr("stroke-dashoffset", totalLength)
                  .transition()
                    .duration(2000)
                    .attr("stroke-dashoffset", 0);*/
            } else if(plot.type === 'band') {
                linesG.append("path")
                    .data([plot.data])
                    .classed(plot.className, true)
                    .attr("d", valueArea);
            } else if(plot.type === 'points') {
                var el = linesG.append("g")
                    .classed(plot.className, true)
                    .selectAll('g')
                    .data(plot.data)
                    .enter()
                    .append('g')
                    .attr('transform', function(d) {
                        return 'translate(' + x(d.date) + ', ' + y(d.close) + ')';
                    });

                var label = el.append('g')
                    .attr('opacity', 0);

                el
                    .append('polygon')
                    .attr('points', function() {
                        if(plot.shape === 'triangle') {
                            return '0,-10 -10,10 10,10';
                        } else {
                            console.error('shape ', plot.shape, ' not yet supported');
                            return '';
                        }
                    })
                    .on('mouseover', function() {
                        d3.select(this.parentElement).select('g')
                            .transition()
                            .attr('opacity', 1);
                        for(let plot of plotData.filter(plot => plot.hover)) {
                            if(plot.hover) {
                                if(plot.type === 'line') {
                                    if(plot.hover.showValue) {
                                        plot.hover.showValueNode.attr('opacity', 0);
                                        plot.hover.markNode.select('rect').attr('opacity', 0);
                                    }
                                }
                            }
                        }
                    })
                    .on('mouseout', function() {
                        d3.select(this.parentElement).select('g')
                            .transition()
                            .attr('opacity', 0);
                        for(let plot of plotData.filter(plot => plot.hover)) {
                            if(plot.hover) {
                                if(plot.type === 'line') {
                                    if(plot.hover.showValue) {
                                        plot.hover.showValueNode.attr('opacity', 1);
                                        plot.hover.markNode.select('rect').attr('opacity', 1);
                                    }
                                }
                            }
                        }
                    });

                label.append('rect')
                    .attr('fill', 'rgba(255,255,255,0.5)')
                    .attr('stroke', '#ccc')
                    .attr('y', -15)
                    .attr('rx', 10)
                    .attr('ry', 10)
                    .attr('x', d => x(d.date) < width * 3/4 ? 20 : -d.label.length * 8 - 10)
                    .attr('height', 30)
                    .attr('width', d => d.label.length * 8);

                label.append('text')
                    .text(d => d.label)
                    .attr('x', d => x(d.date) < width * 3/4 ? 26 : -d.label.length * 8)
                    .attr('y', 6);
            }
        }

        if(animatedOn) {
            linesG.append('rect')
                .attr('height', height)
                .attr('width', width)
                .attr('fill', '#fff')
                .attr('x', 0)
                .transition()
                .duration(1000)
                .attr('width', 0)
                .attr('x', width);
        }


        svg.select('.x-axis')
            .call(d3.axisBottom(x).ticks(6));

        svg.select('.y-axis')
            .call(d3.axisLeft(y).ticks(8));
    };
};

var Animation = function(duration, onTick, onEnd) {
    var tStart;
    var tEnd;

    this.start = function() {
        tStart = performance.now();
        tEnd = tStart + duration;
        this.tick();
    };

    this.tick = function() {
        var t = performance.now();
        var percentage = (t - tStart) / duration;
        if(percentage > 1) {
            percentage = 1;
        }
        onTick(percentage);

        if(t < tEnd) {
            requestAnimationFrame(() => this.tick());
        } else if(onEnd) {
            onEnd();
        }
    };
};