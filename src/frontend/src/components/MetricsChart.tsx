import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { MetricsData } from '../types';

interface Props {
  data: MetricsData[];
}

const MetricsChart: React.FC<Props> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data.length || !svgRef.current) return;

    // Clear previous chart
    d3.select(svgRef.current).selectAll('*').remove();

    // Set dimensions
    const margin = { top: 20, right: 30, bottom: 30, left: 60 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Set scales
    const x = d3.scaleTime()
      .domain(d3.extent(data, d => new Date(d.timestamp)) as [Date, Date])
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.latency) as number])
      .range([height, 0]);

    const y2 = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.users) as number])
      .range([height, 0]);

    // Add X axis
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x));

    // Add Y axis for latency
    svg.append('g')
      .call(d3.axisLeft(y))
      .append('text')
      .attr('fill', '#000')
      .attr('transform', 'rotate(-90)')
      .attr('y', 6)
      .attr('dy', '0.71em')
      .attr('text-anchor', 'end')
      .text('Latency (ms)');

    // Add Y axis for users
    svg.append('g')
      .attr('transform', `translate(${width}, 0)`)
      .call(d3.axisRight(y2))
      .append('text')
      .attr('fill', '#000')
      .attr('transform', 'rotate(90)')
      .attr('y', -6)
      .attr('dy', '0.71em')
      .attr('text-anchor', 'start')
      .text('Users');

    // Add latency line
    const latencyLine = d3.line<MetricsData>()
      .x(d => x(new Date(d.timestamp)))
      .y(d => y(d.latency));

    svg.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', 'steelblue')
      .attr('stroke-width', 1.5)
      .attr('d', latencyLine);

    // Add users line
    const usersLine = d3.line<MetricsData>()
      .x(d => x(new Date(d.timestamp)))
      .y(d => y2(d.users));

    svg.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', 'red')
      .attr('stroke-width', 1.5)
      .attr('d', usersLine);

    // Add legend
    const legend = svg.append('g')
      .attr('font-family', 'sans-serif')
      .attr('font-size', 10)
      .attr('text-anchor', 'start')
      .selectAll('g')
      .data(['Latency', 'Users'])
      .enter().append('g')
      .attr('transform', (d, i) => `translate(0,${i * 20})`);

    legend.append('rect')
      .attr('x', width - 19)
      .attr('width', 19)
      .attr('height', 19)
      .attr('fill', (d, i) => i === 0 ? 'steelblue' : 'red');

    legend.append('text')
      .attr('x', width - 24)
      .attr('y', 9.5)
      .attr('dy', '0.32em')
      .text(d => d);

  }, [data]);

  return <svg ref={svgRef}></svg>;
};

export default MetricsChart;
