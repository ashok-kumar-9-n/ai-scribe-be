from flask import current_app

class GlobalLogger:
    def log_event(self, data=None, level="info", event_name="log_event", distinct_id="default"):
        try:
            log_message = {
                "event": event_name,
                "level": level,
                "distinct_id": distinct_id,
                "data": data,
            }
            logger = current_app.logger
            log_method = getattr(logger, level, logger.info)
            log_method(log_message)
        except Exception as e:
            print(f"Logging failed: {e} | Data: {data}")

# Global instance
global_logger = GlobalLogger()
