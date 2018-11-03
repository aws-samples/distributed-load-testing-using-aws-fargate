// Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
const elasticsearch = require('elasticsearch');
const awsElasticSearch = require('http-aws-es');
const ChanceJs = require('chance');
const chance = new ChanceJs();

describe('Elasticsearch Document Consumer', () => {

  const elasticSearchUrl = 'https://banana.us-west-2.es.amazonaws.com';
  const index = 'performance-testing';
  const client = new elasticsearch.Client({
    hosts: [elasticSearchUrl],
    connectionClass: awsElasticSearch,
    apiVersion: "6.3",
  });

  it('searches documents based on random text', () => {
    return client.search({
      index: index,
      q: chance.word(),
    });
  });
});