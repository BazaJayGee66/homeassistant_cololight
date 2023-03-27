#!/bin/bash

RELEASE_VERSION=$(buildkite-agent meta-data get release-version)
RELEASE_NOTES=$(buildkite-agent meta-data get release-notes)

echo "+++ :rocket: Releasing version ${RELEASE_VERSION}"

touch custom_components/cololight/${RELEASE_VERSION}

cd custom_components &&\
zip -r cololight.zip \
    cololight \
    -x "*/__pycache__/*"

gh release create \
    --prerelease \
    ${RELEASE_VERSION} \
    'cololight.zip' \
    -t ${RELEASE_VERSION} \
    -n "${RELEASE_NOTES}" \
    --repo 'BazaJayGee66/homeassistant_cololight'
