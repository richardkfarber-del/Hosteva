# Spider-Man's Technical Memory

## API Integrations
### Google Veo 3.1 API (2026 Specification)
- **Endpoint**: Veo 3.1 video generation is hosted under the `v1beta` route. It requires the `predictLongRunning` endpoint (e.g., `models/veo-3.1-fast-generate-preview:predictLongRunning`). Standard `/v1/models/{model}:generateContent` will fail with a 404.
- **Payload Structure**: Veo uses a Vertex-style payload requiring `instances` (array of objects with `prompt`) and `parameters` (aspectRatio, resolution, durationSeconds).
- **Response Structure**: Veo is asynchronous. The `predictLongRunning` call returns an operation ID. You must poll `base_url/operations/{operation_name}` until `done` is True.
- **Media Download**: The final URL is nested deeply inside the operation status object: `status_data['response']['generateVideoResponse']['generatedSamples'][0]['video']['uri']`. 
- **Authentication**: When downloading the raw `.mp4` file from the returned URI, the `key={API_KEY}` parameter MUST be appended to the URL to bypass Google's storage authentication block.

## Process Failures
- **BUG-001**: Failed to correctly implement the Veo 3.1 polling and URI download structure. Orchestrator (Fury) had to manually patch the script due to syntax errors in parsing the deeply nested JSON response from Google.
- **Lesson Learned**: Always `print()` and inspect raw JSON payloads from new/alpha Google APIs before writing dict-traversal code.
