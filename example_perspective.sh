curl -H "Content-Type: application/json" --data \
	    '{comment: {text: "what kind of idiot name is foo?"},
      languages: ["en"],
            requestedAttributes: {TOXICITY:{}} }' \
		        https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=AIzaSyDcjiXdtrCLz_qTabKcDW9J-2nUFXHGU3w
