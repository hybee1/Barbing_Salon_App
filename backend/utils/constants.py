




class SalonBusinessHour:

    @staticmethod
    def business_hours():

        from backend.salon_settings import services_salon_config

        salon_config = services_salon_config.get_salon_info_config()
        BUSINESS_OPEN_TIME = salon_config["open_time"]
        BUSINESS_CLOSE_TIME = salon_config["close_time"]
        return BUSINESS_OPEN_TIME, BUSINESS_CLOSE_TIME


