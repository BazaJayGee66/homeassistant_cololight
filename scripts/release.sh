#!/bin/bash

RELEASE_VERSION=$(buildkite-agent meta-data get release-version)
RELEASE_NOTES=$(buildkite-agent meta-data get release-notes)

echo "+++ :rocket: Releasing version ${RELEASE_VERSION}"
zip -r cololight.zip \
    custom_components/cololight \
    -x "*/__pycache__/*"

gh auth login --with-token <<< "${GITHUB_TOKEN}"

gh release create \
    ${RELEASE_VERSION} \
    'cololight.zip' \
    -t ${RELEASE_VERSION} \
    -n ${RELEASE_NOTES}