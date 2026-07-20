#!/usr/bin/env python3
"""Replace renderWorldFlow function in index.html with country-level version."""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the entire renderWorldFlow function
old_func = '''async function renderWorldFlow() {
  await loadData();
  if (!Data.species_341) return;

  const container = document.getElementById('world-flow-chart');
  worldFlowChart = echarts.init(container);

  // Count origins from species_341 using origin_continent
  const totalSpecies = Data.species_341.length;
  const americaCount = Data.species_341.filter(s => s.origin_continent === '美洲').length;
  const europeCount = Data.species_341.filter(s => s.origin_continent === '欧洲').length;
  const asiaCount = Data.species_341.filter(s => s.origin_continent === '亚洲').length;
  const africaCount = Data.species_341.filter(s => s.origin_continent === '非洲').length;
  const oceaniaCount = Data.species_341.filter(s => s.origin_continent === '大洋洲').length;
  const otherCount = Data.species_341.filter(s => s.origin_continent === '其他').length;

  // Geographic coordinates for each origin (realistic lon, lat)
  const originCoords = {
    '美洲': [-80, 15],
    '欧洲': [10, 50],
    '亚洲': [70, 35],
    '非洲': [20, 5],
    '大洋洲': [135, -25],
    '其他': [-30, -10],
    '中国': [105, 35]
  };

  const colors = {
    '美洲': '#DC2626',
    '欧洲': '#3B82F6',
    '亚洲': '#8B5CF6',
    '非洲': '#F59E0B',
    '大洋洲': '#10B981',
    '其他': '#64748B',
    '中国': '#EF4444'
  };

  // Build accurate origin counts from species_341
  const originCounts = {
    '美洲': americaCount,
    '欧洲': europeCount,
    '亚洲': asiaCount,
    '非洲': africaCount,
    '大洋洲': oceaniaCount,
    '其他': otherCount,
    '中国': totalSpecies
  };

  // Update flow stats dynamically
  const stats = [
    { num: americaCount, lbl: '来自美洲' },
    { num: europeCount, lbl: '来自欧洲' },
    { num: asiaCount, lbl: '来自亚洲' },
    { num: africaCount, lbl: '来自非洲' },
    { num: oceaniaCount + otherCount, lbl: '大洋洲/其他' }
  ];
  const flowInsight = document.querySelector('.flow-insight');
  if (flowInsight) {
    flowInsight.innerHTML = stats.map(s => `
      <div class="flow-stat"><div class="fs-num">${s.num}</div><div class="fs-lbl">${s.lbl}</div></div>
    `).join('');
  }

  // Flow data - all continents pointing to China
  const flowLinks = Object.keys(originCounts).filter(k => k !== '中国').map(k => ({
    source: k, target: '中国', value: originCounts[k], color: colors[k]
  }));

  // Try to load world map GeoJSON
  const hasWorldMap = await loadWorldGeoJSON();

  if (hasWorldMap) {
    // Real world map visualization
    const linesData = flowLinks.map(d => ({
      coords: [originCoords[d.source], originCoords[d.target]],
      lineStyle: {
        width: Math.max(2, d.value / 8),
        color: d.color,
        opacity: 0.7,
        curveness: 0.2
      }
    }));

    const scatterData = Object.keys(originCoords).map(name => ({
      name: name,
      value: [...originCoords[name], originCounts[name] || 0],
      itemStyle: { color: colors[name] },
      label: {
        show: true,
        formatter: function(p) {
          const val = originCounts[p.name] || 0;
          return `{name|${p.name}}\\n{val|${val}种}`;
        },
        rich: {
          name: { color: '#E8F0EB', fontSize: 12, lineHeight: 18, fontWeight: 700 },
          val: { color: '#F59E0B', fontSize: 11, lineHeight: 16, fontWeight: 600 }
        },
        position: name === '中国' ? 'right' : 'bottom',
        distance: 8
      }
    }));

    worldFlowChart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        formatter: function(p) {
          if (p.seriesType === 'effectScatter') {
            const val = originCounts[p.name] || 0;
            return `<strong>${p.name}</strong><br/>` +
              (p.name === '中国' ? '入侵物种目标地' : `原产地：${val}种`);
          }
          if (p.seriesType === 'lines') {
            const link = flowLinks[p.dataIndex];
            return `<strong>${link.source} → ${link.target}</strong><br/>物种数量：${link.value}种`;
          }
          return '';
        }
      },
      geo: {
        map: 'world',
        roam: true,
        silent: true,
        itemStyle: {
          areaColor: '#132820',
          borderColor: '#1F3D30',
          borderWidth: 0.5
        },
        emphasis: { disabled: true },
        center: [30, 20],
        zoom: 1.2
      },
      series: [
        {
          type: 'lines',
          coordinateSystem: 'geo',
          data: linesData,
          effect: {
            show: true,
            period: 4,
            trailLength: 0.5,
            color: '#F59E0B',
            symbol: 'arrow',
            symbolSize: 8
          },
          lineStyle: { curveness: 0.2, opacity: 0.6 }
        },
        {
          type: 'effectScatter',
          coordinateSystem: 'geo',
          data: scatterData,
          symbolSize: function(val) {
            return val[2] > 20 ? Math.min(val[2] / 3, 45) : 20;
          },
          label: {
            show: true,
            formatter: function(p) {
              const val = originCounts[p.name] || 0;
              return `{name|${p.name}}\\n{val|${val}种}`;
            },
            rich: {
              name: { color: '#E8F0EB', fontSize: 12, lineHeight: 18, fontWeight: 700 },
              val: { color: '#F59E0B', fontSize: 11, lineHeight: 16, fontWeight: 600 }
            },
            position: function(p) { return p.name === '中国' ? 'right' : 'bottom'; },
            distance: 8
          },
          itemStyle: { color: function(p) { return colors[p.name] || '#94A3B8'; } },
          rippleEffect: { brushType: 'stroke', scale: 3 }
        }
      ]
    });
  } else {
    // Fallback: graph layout with geographic-like coordinates
    const regions = [
      { name: '美洲', x: 100, y: 200, color: '#DC2626' },
      { name: '欧洲', x: 380, y: 110, color: '#3B82F6' },
      { name: '亚洲', x: 500, y: 180, color: '#8B5CF6' },
      { name: '非洲', x: 390, y: 300, color: '#F59E0B' },
      { name: '大洋洲', x: 680, y: 340, color: '#10B981' },
      { name: '其他', x: 80, y: 340, color: '#64748B' },
      { name: '中国', x: 630, y: 160, color: '#EF4444' }
    ];

    worldFlowChart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        formatter: function(p) {
          if (p.dataType === 'node') {
            const val = originCounts[p.name] || 0;
            return `<strong>${p.name}</strong><br/>` +
              (p.name === '中国' ? '入侵物种目标地' : `原产地：${val}种`);
          }
          if (p.dataType === 'edge') {
            return `<strong>${p.data.source} → ${p.data.target}</strong><br/>物种数量：${p.data.value}种`;
          }
          return '';
        }
      },
      xAxis: { show: false, min: 0, max: 800 },
      yAxis: { show: false, min: 0, max: 400 },
      series: [{
        type: 'graph',
        layout: 'none',
        coordinateSystem: 'cartesian2d',
        data: regions.map(r => ({
          name: r.name,
          value: [r.x, r.y],
          symbolSize: r.name === '中国' ? 60 : 35,
          itemStyle: { color: r.color },
          label: {
            show: true,
            formatter: function(p) {
              const val = originCounts[p.name] || 0;
              return `{name|${p.name}}\\n{val|${val}种}`;
            },
            rich: {
              name: { color: '#E8F0EB', fontSize: 12, lineHeight: 18, fontWeight: 700 },
              val: { color: '#F59E0B', fontSize: 11, lineHeight: 16, fontWeight: 600 }
            }
          }
        })),
        links: flowLinks.map(d => ({
          source: d.source, target: d.target, value: d.value,
          lineStyle: { width: Math.max(2, d.value / 8), color: d.color },
          label: { show: true, formatter: '{c}种', fontSize: 10, color: '#F59E0B' }
        })),
        lineStyle: { curveness: 0.3, opacity: 0.6 },
        emphasis: { focus: 'adjacent', lineStyle: { width: 4 } },
        label: { show: true, fontSize: 11, color: '#E8F0EB' },
        animationDuration: 2000,
        animationEasing: 'elasticOut'
      }]
    });
  }
}'''

new_func = '''async function renderWorldFlow() {
  await loadData();
  if (!Data.worldFlowCountries) return;

  const container = document.getElementById('world-flow-chart');
  worldFlowChart = echarts.init(container);

  const countries = Data.worldFlowCountries;
  const chinaNode = countries.find(function(c) { return c.name === '中国'; });
  const sourceNodes = countries.filter(function(c) { return c.name !== '中国'; });

  // Continent color mapping
  var continentColor = {
    '美洲': '#DC2626', '欧洲': '#3B82F6', '亚洲': '#8B5CF6',
    '非洲': '#F59E0B', '大洋洲': '#10B981', '其他': '#64748B'
  };
  var countryContinent = {
    '美国': '美洲', '加拿大': '美洲', '墨西哥': '美洲', '巴西': '美洲', '阿根廷': '美洲',
    '智利': '美洲', '秘鲁': '美洲', '哥伦比亚': '美洲', '委内瑞拉': '美洲', '古巴': '美洲',
    '英国': '欧洲', '法国': '欧洲', '德国': '欧洲', '西班牙': '欧洲', '意大利': '欧洲',
    '希腊': '欧洲', '俄罗斯': '欧洲',
    '印度': '亚洲', '日本': '亚洲', '韩国': '亚洲', '印度尼西亚': '亚洲', '马来西亚': '亚洲',
    '泰国': '亚洲', '菲律宾': '亚洲', '越南': '亚洲', '伊朗': '亚洲', '土耳其': '亚洲',
    '伊拉克': '亚洲', '沙特阿拉伯': '亚洲', '巴基斯坦': '亚洲', '孟加拉国': '亚洲', '不丹': '亚洲',
    '南非': '非洲', '马达加斯加': '非洲', '肯尼亚': '非洲', '安哥拉': '非洲', '尼日利亚': '非洲',
    '埃及': '非洲', '埃塞俄比亚': '非洲',
    '澳大利亚': '大洋洲', '新西兰': '大洋洲'
  };

  // Update flow stats by continent
  var continentCounts = {};
  sourceNodes.forEach(function(n) {
    var cont = countryContinent[n.name] || '其他';
    continentCounts[cont] = (continentCounts[cont] || 0) + n.value;
  });
  var stats = [
    { num: continentCounts['美洲'] || 0, lbl: '来自美洲' },
    { num: continentCounts['欧洲'] || 0, lbl: '来自欧洲' },
    { num: continentCounts['亚洲'] || 0, lbl: '来自亚洲' },
    { num: continentCounts['非洲'] || 0, lbl: '来自非洲' },
    { num: (continentCounts['大洋洲'] || 0) + (continentCounts['其他'] || 0), lbl: '大洋洲/其他' }
  ];
  var flowInsight = document.querySelector('.flow-insight');
  if (flowInsight) {
    flowInsight.innerHTML = stats.map(function(s) {
      return '<div class="flow-stat"><div class="fs-num">' + s.num + '</div><div class="fs-lbl">' + s.lbl + '</div></div>';
    }).join('');
  }

  // Try to load world map GeoJSON
  var hasWorldMap = await loadWorldGeoJSON();

  if (hasWorldMap) {
    // Build lines from each country to China
    var linesData = sourceNodes.map(function(n) {
      return {
        coords: [n.coord, chinaNode.coord],
        lineStyle: {
          width: Math.max(1, n.value / 20),
          color: continentColor[countryContinent[n.name] || '其他'],
          opacity: 0.45,
          curveness: 0.15
        }
      };
    });

    // Scatter data for all countries
    var scatterData = countries.map(function(n) {
      var isChina = n.name === '中国';
      var cont = countryContinent[n.name] || '其他';
      return {
        name: n.name,
        value: [n.coord[0], n.coord[1], n.value],
        itemStyle: {
          color: isChina ? '#EF4444' : (continentColor[cont] || '#94A3B8')
        },
        label: {
          show: n.value >= 5 || isChina,
          formatter: function(p) {
            var val = p.value[2];
            return '{name|' + p.name + '}\\n{val|' + val + '种}';
          },
          rich: {
            name: { color: '#E8F0EB', fontSize: 11, lineHeight: 16, fontWeight: 700 },
            val: { color: '#F59E0B', fontSize: 10, lineHeight: 14, fontWeight: 600 }
          },
          position: isChina ? 'right' : 'bottom',
          distance: 6
        }
      };
    });

    worldFlowChart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        formatter: function(p) {
          if (p.seriesType === 'effectScatter') {
            var val = p.value[2];
            return '<strong>' + p.name + '</strong><br/>' +
              (p.name === '中国' ? '入侵物种目标地<br/>累计341种' : '原产地：' + val + '种');
          }
          if (p.seriesType === 'lines') {
            return '<strong>' + p.data.from + ' → 中国</strong><br/>物种数量：' + p.data.value + '种';
          }
          return '';
        }
      },
      geo: {
        map: 'world',
        roam: true,
        silent: true,
        itemStyle: {
          areaColor: '#132820',
          borderColor: '#1F3D30',
          borderWidth: 0.5
        },
        emphasis: { disabled: true },
        center: [30, 20],
        zoom: 1.2
      },
      series: [
        {
          type: 'lines',
          coordinateSystem: 'geo',
          data: linesData,
          effect: {
            show: true,
            period: 4,
            trailLength: 0.5,
            color: '#F59E0B',
            symbol: 'arrow',
            symbolSize: 5
          },
          lineStyle: { curveness: 0.15, opacity: 0.45 }
        },
        {
          type: 'effectScatter',
          coordinateSystem: 'geo',
          data: scatterData,
          symbolSize: function(val) {
            if (val[2] >= 100) return Math.min(val[2] / 4, 50);
            if (val[2] >= 20) return val[2] / 3;
            return Math.max(6, val[2] / 2);
          },
          label: {
            show: true,
            formatter: function(p) {
              var val = p.value[2];
              return '{name|' + p.name + '}\\n{val|' + val + '种}';
            },
            rich: {
              name: { color: '#E8F0EB', fontSize: 11, lineHeight: 16, fontWeight: 700 },
              val: { color: '#F59E0B', fontSize: 10, lineHeight: 14, fontWeight: 600 }
            },
            position: function(p) { return p.name === '中国' ? 'right' : 'bottom'; },
            distance: 6
          },
          itemStyle: { color: function(p) {
            return p.name === '中国' ? '#EF4444' : (continentColor[countryContinent[p.name] || '其他'] || '#94A3B8');
          }},
          rippleEffect: { brushType: 'stroke', scale: 3 }
        }
      ]
    });
  } else {
    // Fallback: simple graph with all countries
    var fallbackNodes = countries.map(function(n) {
      var cont = countryContinent[n.name] || '其他';
      var color = n.name === '中国' ? '#EF4444' : (continentColor[cont] || '#94A3B8');
      // Simple projection: lng 73-135, lat 18-54 for China area, spread others
      var x = ((n.coord[0] + 180) / 360) * 800;
      var y = ((90 - n.coord[1]) / 180) * 400;
      return {
        name: n.name,
        value: [x, y],
        symbolSize: n.name === '中国' ? 60 : Math.max(8, n.value / 3),
        itemStyle: { color: color },
        label: {
          show: n.value >= 5 || n.name === '中国',
          formatter: function(p) {
            var node = countries.find(function(c) { return c.name === p.name; });
            return '{name|' + p.name + '}\\n{val|' + (node ? node.value : 0) + '种}';
          },
          rich: {
            name: { color: '#E8F0EB', fontSize: 11, lineHeight: 16, fontWeight: 700 },
            val: { color: '#F59E0B', fontSize: 10, lineHeight: 14, fontWeight: 600 }
          }
        }
      };
    });
    var fallbackLinks = sourceNodes.map(function(n) {
      var cont = countryContinent[n.name] || '其他';
      return {
        source: n.name, target: '中国', value: n.value,
        lineStyle: { width: Math.max(1, n.value / 20), color: continentColor[cont] || '#94A3B8' }
      };
    });

    worldFlowChart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        formatter: function(p) {
          if (p.dataType === 'node') {
            var node = countries.find(function(c) { return c.name === p.name; });
            return '<strong>' + p.name + '</strong><br/>' +
              (p.name === '中国' ? '入侵物种目标地' : '原产地：' + (node ? node.value : 0) + '种');
          }
          if (p.dataType === 'edge') {
            return '<strong>' + p.data.source + ' → ' + p.data.target + '</strong><br/>物种数量：' + p.data.value + '种';
          }
          return '';
        }
      },
      xAxis: { show: false, min: 0, max: 800 },
      yAxis: { show: false, min: 0, max: 400 },
      series: [{
        type: 'graph',
        layout: 'none',
        coordinateSystem: 'cartesian2d',
        data: fallbackNodes,
        links: fallbackLinks,
        lineStyle: { curveness: 0.3, opacity: 0.5 },
        emphasis: { focus: 'adjacent', lineStyle: { width: 4 } },
        label: { show: true, fontSize: 11, color: '#E8F0EB' },
        animationDuration: 2000,
        animationEasing: 'elasticOut'
      }]
    });
  }
}'''

if old_func not in content:
    print('ERROR: Could not find old function!')
    exit(1)

content = content.replace(old_func, new_func)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('OK: renderWorldFlow replaced successfully.')
