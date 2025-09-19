#!/bin/bash
if [ ! -f "users.db" ]; then
    touch users.db
    chmod 664 users.db
fi