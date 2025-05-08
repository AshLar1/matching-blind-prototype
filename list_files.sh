#!/bin/bash

echo "📁 Listing all folders and files in your Replit environment:"
echo "-----------------------------------------------------------"
find . -type d -print -o -type f -print | sort
