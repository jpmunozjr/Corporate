#!/bin/bash

for i in rx tx sg tso ufo gso gro lro; do ethtool -K INTERFACE_NAME $i off; done
