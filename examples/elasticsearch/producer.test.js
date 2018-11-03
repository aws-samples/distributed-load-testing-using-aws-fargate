// Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
const elasticsearch = require('elasticsearch');
const awsElasticSearch = require('http-aws-es');
const ChanceJs = require('chance');
const chance = new ChanceJs();

describe('Elasticsearch Document Producer', () => {

  const elasticSearchUrl = 'https://banana.us-west-2.es.amazonaws.com';
  const index = 'performance-testing';
  const client = new elasticsearch.Client({
    hosts: [elasticSearchUrl],
    connectionClass: awsElasticSearch,
    apiVersion: "6.3",
  });

  it('stores a JSON document', () => {
    return client.index({
      index: index,
      type: 'dummyType',
      id: chance.hash(),
      body: {
        name: chance.first(),
        created: new Date().getTime(),
        description: chance.paragraph(),
      },
    });
  });
});