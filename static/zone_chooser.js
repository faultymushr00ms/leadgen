/* Overlap picker for community polygons on the map.
   Leaflet delivers a click to the top shape only. These helpers find every
   polygon that actually contains the point, smallest first. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.ForgeZoneChooser = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  var KIND_RANK = {municipality: 0, township: 1, county: 2};

  function norm(value) {
    return String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  }

  function boundaryKind(boundary) {
    var text = norm(boundary);
    if (text.indexOf('township') !== -1) return 'township';
    if (text.indexOf('county') !== -1) return 'county';
    return 'municipality';
  }

  function ringContains(ring, lon, lat) {
    var inside = false;
    if (!ring || !ring.length) return false;
    var j = ring.length - 1;
    for (var i = 0; i < ring.length; i++) {
      var point = ring[i];
      var previous = ring[j];
      if (!point || !previous || point.length < 2 || previous.length < 2) {
        j = i;
        continue;
      }
      var xi = point[0];
      var yi = point[1];
      var xj = previous[0];
      var yj = previous[1];
      if ((yi > lat) !== (yj > lat)) {
        var denom = (yj - yi) || 1e-15;
        if (lon < ((xj - xi) * (lat - yi)) / denom + xi) inside = !inside;
      }
      j = i;
    }
    return inside;
  }

  function polygonContains(rings, lon, lat) {
    if (!rings || !rings.length || !ringContains(rings[0], lon, lat)) return false;
    for (var i = 1; i < rings.length; i++) {
      if (ringContains(rings[i], lon, lat)) return false;
    }
    return true;
  }

  function geometryContains(geometry, lon, lat) {
    if (!geometry) return false;
    var kind = geometry.type;
    var coords = geometry.coordinates || [];
    if (kind === 'Polygon') return polygonContains(coords, lon, lat);
    if (kind === 'MultiPolygon') {
      for (var i = 0; i < coords.length; i++) {
        if (polygonContains(coords[i], lon, lat)) return true;
      }
    }
    return false;
  }

  function ringSignedArea(ring) {
    if (!ring || ring.length < 3) return 0;
    var points = ring;
    var last = points[points.length - 1];
    var first = points[0];
    if (last && first && last[0] === first[0] && last[1] === first[1]) {
      points = points.slice(0, -1);
    }
    if (points.length < 3) return 0;
    var sum = 0;
    for (var i = 0, n = points.length; i < n; i++) {
      var current = points[i];
      var next = points[(i + 1) % n];
      if (!current || !next || current.length < 2 || next.length < 2) continue;
      sum += current[0] * next[1] - next[0] * current[1];
    }
    return sum / 2;
  }

  function polygonArea(rings) {
    if (!rings || !rings.length) return 0;
    var area = Math.abs(ringSignedArea(rings[0]));
    for (var i = 1; i < rings.length; i++) area -= Math.abs(ringSignedArea(rings[i]));
    return area > 0 ? area : 0;
  }

  function geometryArea(geometry) {
    if (!geometry) return 0;
    var coords = geometry.coordinates || [];
    if (geometry.type === 'Polygon') return polygonArea(coords);
    if (geometry.type === 'MultiPolygon') {
      var total = 0;
      for (var i = 0; i < coords.length; i++) total += polygonArea(coords[i]);
      return total;
    }
    return 0;
  }

  function compareHits(a, b) {
    var areaA = a.area > 0 ? a.area : Infinity;
    var areaB = b.area > 0 ? b.area : Infinity;
    if (areaA !== areaB) return areaA - areaB;
    var rank = (KIND_RANK[boundaryKind(a.boundary)] || 0) - (KIND_RANK[boundaryKind(b.boundary)] || 0);
    if (rank) return rank;
    var byName = String(a.name || '').localeCompare(String(b.name || ''));
    if (byName) return byName;
    return String(a.agg || '').localeCompare(String(b.agg || ''));
  }

  function featuresAtPoint(features, lon, lat) {
    var hits = [];
    var list = features || [];
    for (var i = 0; i < list.length; i++) {
      var feature = list[i] || {};
      if (!geometryContains(feature.geometry, lon, lat)) continue;
      var props = feature.properties || {};
      hits.push({
        index: i,
        name: props.name || 'Community',
        boundary: props.boundary || '',
        agg: props.agg || '',
        county: props.county || '',
        area: geometryArea(feature.geometry),
        properties: props
      });
    }
    hits.sort(compareHits);
    return hits;
  }

  function chooseAction(hits) {
    return hits && hits.length > 1 ? 'chooser' : 'open';
  }

  function countiesOf(zone) {
    var found = [];
    var list = (zone && zone.counties) || [];
    for (var i = 0; i < list.length; i++) {
      var county = norm(list[i]);
      if (county) found.push(county);
    }
    return found;
  }

  function countyAgrees(zone, county) {
    if (!county) return true;
    var counties = countiesOf(zone);
    if (!counties.length) return norm(zone.name).indexOf(county) !== -1;
    return counties.indexOf(county) !== -1;
  }

  function matchZone(hit, zones) {
    var name = norm(hit.name || (hit.properties && hit.properties.name));
    var county = norm(hit.county || (hit.properties && hit.properties.county));
    var kind = boundaryKind(hit.boundary || (hit.properties && hit.properties.boundary));
    if (!name) return null;
    var scored = [];
    (zones || []).forEach(function (zone) {
      var label = norm(zone && zone.name);
      if (!label) return;
      var score = 99;
      if (kind === 'township') {
        if (label === name + ' township') score = 0;
        else if (label.indexOf(name + ' township ') === 0 && county && label.indexOf(county) !== -1) score = 1;
      } else if (kind === 'county') {
        if (label === name + ' county') score = 0;
        else if (label.indexOf(name + ' county ') === 0) score = 2;
      } else if (label === name && label.indexOf('township') === -1 && label.indexOf('county') === -1) {
        score = 0;
      }
      if (score === 99 || !countyAgrees(zone, county)) return;
      scored.push({score: score, zone: zone});
    });
    if (!scored.length) return null;
    var best = scored[0].score;
    for (var i = 1; i < scored.length; i++) {
      if (scored[i].score < best) best = scored[i].score;
    }
    var top = [];
    for (var j = 0; j < scored.length; j++) {
      if (scored[j].score === best) top.push(scored[j].zone);
    }
    var urls = {};
    top.forEach(function (zone) {
      if (zone.card_url) urls[zone.card_url] = true;
    });
    var urlKeys = Object.keys(urls);
    if (top.length === 1) return top[0];
    if (urlKeys.length === 1) return top[0];
    return null;
  }

  function formatRate(rate) {
    var text = String(rate || '').trim();
    if (!text) return '';
    if (text.indexOf('¢') !== -1) return text;
    if (!/^\d+(\.\d+)?$/.test(text)) return '';
    return text + '¢';
  }

  function safeCardUrl(zone) {
    var url = zone && zone.card_url;
    if (typeof url !== 'string' || url.indexOf('/card?') !== 0) return '';
    if (url.indexOf('\\') !== -1 || url.indexOf('//') !== -1) return '';
    return url;
  }

  function uniqueBits(bits) {
    var seen = {};
    var kept = [];
    bits.forEach(function (bit) {
      var text = String(bit || '').trim();
      var key = text.toLowerCase();
      if (!text || seen[key]) return;
      seen[key] = true;
      kept.push(text);
    });
    return kept;
  }

  function describeHit(hit, zones, hits) {
    var match = matchZone(hit, zones);
    var label = (match && match.name) || hit.name || 'Community';
    var bits = [];
    if (hit.boundary && norm(label).indexOf(norm(hit.boundary)) === -1) bits.push(hit.boundary);
    var sameShape = (hits || []).filter(function (other) {
      return other.name === hit.name && other.boundary === hit.boundary && other.county === hit.county;
    });
    if (sameShape.length > 1 && hit.agg) bits.push(hit.agg);
    var counties = {};
    (hits || []).forEach(function (other) {
      if (other.name === hit.name && other.boundary === hit.boundary && other.county) {
        counties[other.county] = true;
      }
    });
    if (Object.keys(counties).length > 1 && hit.county && norm(label).indexOf(norm(hit.county)) === -1) {
      bits.push(hit.county + ' County');
    }
    var rate = match ? formatRate(match.rate) : '';
    if (rate) bits.push(rate);
    else if (match && match.category_label) bits.push(match.category_label);
    else if (hit.agg) bits.push(hit.agg);
    var described = uniqueBits(bits);
    return {
      label: label,
      hint: described.join(' · '),
      cardUrl: match ? safeCardUrl(match) : ''
    };
  }

  return {
    norm: norm,
    ringContains: ringContains,
    geometryContains: geometryContains,
    geometryArea: geometryArea,
    compareHits: compareHits,
    featuresAtPoint: featuresAtPoint,
    chooseAction: chooseAction,
    matchZone: matchZone,
    describeHit: describeHit
  };
});
