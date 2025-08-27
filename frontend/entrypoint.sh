#!/bin/sh

# Replace API URL in built React app
if [ -n "$REACT_APP_API_URL" ]; then
    echo "Setting API URL to: $REACT_APP_API_URL"
    
    # Replace the API URL in all JS files
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|http://backend:8000|$REACT_APP_API_URL|g" {} +
    
    # Also replace in any HTML files
    find /usr/share/nginx/html -name "*.html" -exec sed -i "s|http://backend:8000|$REACT_APP_API_URL|g" {} +
fi

# Start nginx
nginx -g "daemon off;"