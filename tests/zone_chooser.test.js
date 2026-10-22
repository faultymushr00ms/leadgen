const test = require('node:test');
const assert = require('node:assert/strict');
const chooser = require('../static/zone_chooser.js');

function rect(name, boundary, county, agg, west, south, east, north) {
  return {
    type: 'Feature',
    properties: {name: name, boundary: boundary, county: county, agg: agg},
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [west, south], [east, south], [east, north], [west, north], [west, south]
      ]]
    }
  };
}

const township = rect('Bath', 'Township', 'Summit', 'Electric', 0, 0, 10, 10);
const city = rect('Fairlawn', 'Municipality', 'Summit', 'Electric', 2, 2, 4, 4);
const neighbor = rect('Copley', 'Township', 'Summit', 'Electric', 9, 9, 14, 14);
const bathGas = rect('Bath', 'Township', 'Summit', 'Gas', 0, 0, 10, 10);

test('a point in one polygon opens directly', function () {
  const hits = chooser.featuresAtPoint([township, city], 1, 1);
  assert.equal(hits.length, 1);
  assert.equal(hits[0].name, 'Bath');
  assert.equal(chooser.chooseAction(hits), 'open');
});

test('a city inside a township lists the smaller zone first', function () {
  const hits = chooser.featuresAtPoint([township, city, neighbor], 3, 3);
  assert.deepEqual(hits.map(function (hit) { return hit.name; }), ['Fairlawn', 'Bath']);
  assert.equal(chooser.chooseAction(hits), 'chooser');
  assert.ok(hits[0].area < hits[1].area);
});

test('adjacent overlap is included and a point in only one is not', function () {
  const overlap = chooser.featuresAtPoint([township, neighbor], 9.5, 9.5);
  assert.deepEqual(overlap.map(function (hit) { return hit.name; }).sort(), ['Bath', 'Copley']);
  const only = chooser.featuresAtPoint([township, neighbor], 1, 1);
  assert.deepEqual(only.map(function (hit) { return hit.name; }), ['Bath']);
  assert.equal(chooser.chooseAction([]), 'open');
});

test('holes and separate parts are respected', function () {
  const holed = {
    type: 'Feature',
    properties: {name: 'County', boundary: 'County', county: 'Summit', agg: 'Electric'},
    geometry: {
      type: 'Polygon',
      coordinates: [
        [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
        [[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]]
      ]
    }
  };
  const island = {
    type: 'Feature',
    properties: {name: 'Island', boundary: 'Municipality', county: 'Summit', agg: 'Electric'},
    geometry: {
      type: 'MultiPolygon',
      coordinates: [[
        [[4.2, 4.2], [5.8, 4.2], [5.8, 5.8], [4.2, 5.8], [4.2, 4.2]]
      ]]
    }
  };
  assert.equal(chooser.geometryContains(holed.geometry, 5, 5), false);
  assert.equal(chooser.geometryContains(holed.geometry, 1, 1), true);
  const hits = chooser.featuresAtPoint([holed, island], 5, 5);
  assert.deepEqual(hits.map(function (hit) { return hit.name; }), ['Island']);
  assert.ok(chooser.geometryArea(holed.geometry) < 100);
  assert.ok(chooser.geometryArea(holed.geometry) > 90);
});

test('rate is the hint when the zone has one, otherwise the program', function () {
  const zones = [
    {name: 'Fairlawn', counties: ['Summit'], rate: '10.399', category_label: 'NOPEC', card_url: '/card?file=akron&name=Fairlawn'},
    {name: 'Bath Township', counties: ['Summit'], rate: '', category_label: 'NOPEC', card_url: '/card?file=akron&name=Bath%20Township'}
  ];
  const hits = chooser.featuresAtPoint([city, township], 3, 3);
  const cityLine = chooser.describeHit(hits[0], zones, hits);
  const townLine = chooser.describeHit(hits[1], zones, hits);
  assert.equal(cityLine.label, 'Fairlawn');
  assert.equal(cityLine.hint, 'Municipality · 10.399¢');
  assert.equal(cityLine.cardUrl, '/card?file=akron&name=Fairlawn');
  assert.equal(townLine.label, 'Bath Township');
  assert.equal(townLine.hint, 'NOPEC');
  assert.equal(townLine.cardUrl, '/card?file=akron&name=Bath%20Township');
});

test('electric and gas of the same community stay distinct', function () {
  const zones = [
    {name: 'Bath Township', counties: ['Summit'], rate: '9.5', category_label: 'NOPEC', card_url: '/card?file=akron&name=Bath%20Township'}
  ];
  const hits = chooser.featuresAtPoint([township, bathGas], 1, 1);
  assert.equal(hits.length, 2);
  const lines = hits.map(function (hit) { return chooser.describeHit(hit, zones, hits).hint; });
  assert.deepEqual(lines.sort(), ['Electric · 9.5¢', 'Gas · 9.5¢']);
});

test('township and city names do not cross-match, and county qualifiers do', function () {
  const zones = [
    {name: 'Green', counties: ['Summit'], rate: '9.24', category_label: 'NOPEC', card_url: '/card?file=akron&name=Green'},
    {name: 'Green Township', counties: ['Hamilton'], rate: '10.299', category_label: 'Dynegy', card_url: '/card?file=duke&name=Green%20Township'},
    {name: 'Springfield Township (Hamilton Co)', counties: ['Hamilton'], rate: '8.1', category_label: 'Dynegy', card_url: '/card?file=duke&name=Springfield%20Hamilton'},
    {name: 'Springfield Township (Mahoning)', counties: ['Mahoning'], rate: '7.2', category_label: 'NOPEC', card_url: '/card?file=youngstown&name=Springfield%20Mahoning'},
    {name: 'Liberty Township (Butler Co)', counties: ['Butler'], rate: '9', category_label: 'Other aggregation', card_url: '/card?file=a&name=Liberty'},
    {name: 'Liberty Township (Butler)', counties: ['Butler'], rate: '8', category_label: 'Other aggregation', card_url: '/card?file=b&name=Liberty'}
  ];
  const greenCity = {name: 'Green', boundary: 'Municipality', county: 'Summit', agg: 'Electric'};
  const greenTwp = {name: 'Green', boundary: 'Township', county: 'Hamilton', agg: 'Electric'};
  const springfield = {name: 'Springfield', boundary: 'Township', county: 'Hamilton', agg: 'Electric'};
  const liberty = {name: 'Liberty', boundary: 'Township', county: 'Butler', agg: 'Electric'};
  assert.equal(chooser.matchZone(greenCity, zones).name, 'Green');
  assert.equal(chooser.matchZone(greenTwp, zones).name, 'Green Township');
  assert.equal(chooser.matchZone(springfield, zones).name, 'Springfield Township (Hamilton Co)');
  assert.equal(chooser.matchZone(liberty, zones), null);
  const described = chooser.describeHit(liberty, zones, [liberty]);
  assert.equal(described.label, 'Liberty');
  assert.equal(described.cardUrl, '');
  assert.equal(described.hint, 'Township · Electric');
  const evil = chooser.describeHit(
    {name: 'Green', boundary: 'Municipality', county: 'Summit'},
    [{name: 'Green', counties: ['Summit'], rate: '9.24', category_label: 'NOPEC', card_url: 'https://evil.example/card'}],
    []
  );
  assert.equal(evil.cardUrl, '');
});
