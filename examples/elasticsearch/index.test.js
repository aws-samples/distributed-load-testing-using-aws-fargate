// Copyright <YEAR> Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
const elasticsearch = require('elasticsearch');
const awsElasticSearch = require('http-aws-es');

describe('Elasticsearch GameDay', function() {

  const elasticSearchUrl = 'https://banana.us-west-2.es.amazonaws.com';
  const client = new elasticsearch.Client({
    hosts: [elasticSearchUrl],
    connectionClass: awsElasticSearch,
    apiVersion: "6.3",
  });

  it('check health of cluster', function (done) {
    return client.cluster.health()
      .then(data => {
        console.log('Health=', data);
        done();
      })
      .catch(err => {
        console.log('Error=', err);
        done();
      });
  });
});