from bson import ObjectId

def _make_json_serializable(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_json_serializable(v) for v in obj]
    return obj

class GlobalLogger:

    def log_event(self, data=None, level="info", event_name="log_event", distinct_id="default"):
        try:
            log_message = {
                "event": event_name,
                "level": level,
                "distinct_id": distinct_id,
                "data": data,
            }
            # Convert to JSON serializable
            log_message = _make_json_serializable(log_message)
            print(log_message) 
        except Exception as e:
            print(f"Logging failed: {e} | Data: {data}")

# Global instance
global_logger = GlobalLogger()
