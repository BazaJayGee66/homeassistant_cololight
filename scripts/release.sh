#!/bin/bash

RELEASE_VERSION=$(buildkite-agent meta-data get release-version)
RELEASE_NOTES=$(buildkite-agent meta-data get release-notes)

echo "+++ :rocket: Releasing version ${RELEASE_VERSION}"

cd custom_components &&\
zip -r cololight.zip \
    cololight \
    -x "*/__pycache__/*"

gh release create \
    ${RELEASE_VERSION} \
    'custom_components/cololight.zip' \
    -t ${RELEASE_VERSION} \
    -n "${RELEASE_NOTES}"
