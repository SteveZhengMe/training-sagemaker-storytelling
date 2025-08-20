# Data source column description

| Column Name | Features | Data Type | Description EN | Description CN |
| - | - | - | - | - |
| YEAR | Y | int | ~ | ~ |
| MONTH | Y | int | ~ | ~ |
| DAY | Y | int | ~ | ~ |
| DAY_OF_WEEK | Y | int | ~ | ~ |
| AIRLINE | Y | str | Airline Identifier | 航空公司 |
| FLIGHT_NUMBER | Y | str | Flight Identifier | 航班号 |
| TAIL_NUMBER | Y | str | Aircraft Identifier | 机型编号（可以查询飞机型号） |
| ORIGIN_AIRPORT | Y | str | Starting Airport | 起飞机场 |
| DESTINATION_AIRPORT | Y | str | Destination Airport | 降落机场 |
| SCHEDULED_DEPARTURE | Y | str/time | Planned Departure Time | 计划起飞时间 |
| DEPARTURE_TIME | N | str/time | WHEEL_OFF - TAXI_OUT | 实际推出时间（离开登机口） |
| DEPARTURE_DELAY | N | int | Total Delay on Departure | 起飞延迟（DEPARTURE_TIME - SCHEDULED_DEPARTURE） |
| TAXI_OUT | N | int | The time duration elapsed between departure from the origin airport gate and wheels off | 推出耗时 |
| WHEELS_OFF | N | int/time | The time point that the aircraft's wheels leave the ground | 实际起飞时间 （轮离地）|
| SCHEDULED_TIME | Y | int | Planned time amount needed for the flight trip | 计划飞行耗时 （分钟） |
| ELAPSED_TIME | N | int | AIR_TIME+TAXI_IN+TAXI_OUT | 登机口至下机口的时间 |
| AIR_TIME | N | int | The time duration between wheels_off and wheels_on time | 纯飞行时间（轮离地到轮着地） |
| DISTANCE | Y | int | Distance between two airports | 距离 |
| WHEELS_ON | N | str/time | The time point that the aircraft's wheels touch on the ground | 实际落地时间 （轮着地） |
| TAXI_IN | N | int | The time duration elapsed between wheels-on and gate arrival at the destination airport | 推入耗时 |
| SCHEDULED_ARRIVAL | Y | str/time | Planned arrival time | 计划落地时间 |
| ARRIVAL_TIME | N | str/time | WHEELS_ON+TAXI_IN | 实际推入时间 |
| ARRIVAL_DELAY | N | int | ARRIVAL_TIME-SCHEDULED_ARRIVAL | 落地延迟 |
| DIVERTED | ~ | bool | Aircraft landed on airport that out of schedule | 是否计划外 |
| CANCELLED | N | bool | Flight Cancelled (1 = cancelled) | 是否取消航班 |
| CANCELLATION_REASON | N | str | Reason for Cancellation of flight: A - Airline/Carrier; B - Weather; C - National Air System; D - Security | 航班取消原因 |
| AIR_SYSTEM_DELAY | N | int | Delay caused by air system | 交通系统原因延迟 |
| SECURITY_DELAY | N | int | Delay caused by security | 安全原因延迟 |
| AIRLINE_DELAY | N | int | Delay caused by the airline | 航线原因延迟 |
| LATE_AIRCRAFT_DELAY | N | int | Delay caused by aircraft | 上班航线延迟 |
| WEATHER_DELAY | N | int | Delay caused by weather | 天气延迟 |