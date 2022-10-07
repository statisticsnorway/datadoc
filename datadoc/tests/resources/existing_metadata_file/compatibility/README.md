# Backwards Compatibility test resources

We store examples of old supported versions of metadata documents in this directory, so we can test to verify that we can still read them into datadoc.

## Usage

- There should exist one directory per supported version
- The directory needs to be named after the version, for example for version 2.3.4 the directory will be called `v2_3_4`
- These are loaded into Datadoc in a parameterised test to verify that they're still supported
