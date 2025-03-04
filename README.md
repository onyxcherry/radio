# Radio

## Schedulable music player

Schedule playing music for adjustable intervals during the day.

## Features

- automatic playing
- accepting/rejecting tracks in library
- proposing new tracks
- validation against tracks count, total scheduled duration etc.
- supports Youtube
- playing module can be run on different computer than the rest

## Architecture

This project was deliberately created with the concept of **ports & adapters architecture** in mind.
These include not only the Kafka message producer and consumer module or the database repository,
but also the playback of songs.  
And finally, the trivial clock, which plays a crucial role in a project that relies on the passage of time.

## Services

The system consists of services listed:

- ~~frontend~~ – TODO,
- backend which serves the user via API (OpenAPI with Swagger – see /docs/),
- player which observes or waits until a next break to play music on,
- message broker (any Kafka-compatible; here Redpanda is used due to simplicity in deployment on-premise)

## Testing

All unit tests can be run as integration tests using real database and real message broker.  
Of course, there are more integration-only tests, but the former approach both reduces duplicated tests code and allows to debug problem with failures within memory (thus without external dependencies). What a relief!

### Run in Docker by Docker Compose

The only requirement is Docker Compose installed.

Run

```shell
docker compose -f docker-compose.tests.yaml up --abort-on-container-failure backend-integration
```

Want to run another tests (scope or level)?  
Simply change the last argument to any of:

- backend-units
- backend-integration
- player-units
- player-integration

No complex commands passed as execution arguments are needed – all of them are written in docker-compose.tests.yaml.

The command returns a non-zero exit code in case of fail apart from tests result in standard output logged.

#### Example output

```shell
$ docker compose -f docker-compose.tests.yaml up --abort-on-container-failure backend-integration
[+] Running 3/0
 ✔ Container redpanda-broker-0-tests    Created                                                                    0.0s
 ✔ Container init-backend-tests         Created                                                                    0.0s
 ✔ Container backend-tests-integration  Created                                                                    0.0s
Attaching to backend-tests-integration
backend-tests-integration  | ============================= test session starts ==============================
backend-tests-integration  | platform linux -- Python 3.12.4, pytest-8.3.4, pluggy-1.5.0
backend-tests-integration  | rootdir: /app/src
backend-tests-integration  | configfile: pyproject.toml
backend-tests-integration  | plugins: anyio-4.8.0, asyncio-0.25.3
backend-tests-integration  | asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=function
backend-tests-integration  | collected 64 items
backend-tests-integration  |
backend-tests-integration  | src/tests/unit/test_duration.py ...                                      [  4%]
backend-tests-integration  | src/tests/unit/test_events_exchange.py .......                           [ 15%]
backend-tests-integration  | src/tests/unit/test_library.py ..                                        [ 18%]
backend-tests-integration  | src/tests/unit/test_library_repository.py ......                         [ 28%]
backend-tests-integration  | src/tests/unit/test_playlist.py ......                                   [ 37%]
backend-tests-integration  | src/tests/unit/test_playlist_repository.py .......                       [ 48%]
backend-tests-integration  | src/tests/unit/test_provider_youtube.py .........                        [ 62%]
backend-tests-integration  | src/tests/unit/test_requests.py ..................                       [ 90%]
backend-tests-integration  | src/tests/unit/test_track_builder.py ......                              [100%]
backend-tests-integration  |
backend-tests-integration  | ======================== 64 passed, 0 warnings in 6.99s ========================
backend-tests-integration exited with code 0
```

### Run without Docker

- firstly, run Kafka broker

    ```shell
    docker compose up -d redpanda-0
    ```

- backend

    Setup the virtual environment

    ```shell
    cd backend/ && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && pip install -e .
    ```

    Run unit tests

    ```shell
    pytest
    ```

    Run integration tests

    ```shell
    pytest --realdb --realmsgbroker src/tests/
    ```

- player

    Setup the virtual environment

    ```shell
    cd player/ && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && pip install -e .
    ```

    Run unit tests

    ```shell
    pytest
    ```

    Run integration tests

    ```shell
    pytest --realdb --realmsgbroker tests/
    ```

## Production running (on-premise)

Backend service needs Youtube APIv3 token written to [.youtube-api-key.secret](.youtube-api-key.secret) file (its value only).  
Go to the [APIs & Services dashboard](https://console.cloud.google.com/apis/dashboard) to generate the token.

### On single machine

As simple as

```shell
docker compose up -d
```

### On different machines

- on one (main) machine which serves users

    ```shell
    docker compose up -d backend redpanda-0
    ```

- on second machine (with speakers connected)

    ```shell
    docker compose up -d player
    ```

    moreover, you may need to change interface on which backend and Kafka ports are exposed (with recommendation of VPN usage for the network)
    and – depending on DNS resolver configuration – also the hostnames of broker and schema registry defined in [.env.compose](.env.compose).

### Playback devices

#### WSL2

WSL2 users can play music within Docker container if they use wslg and have `/mnt/wslg/{PulseServer,PulseAudioRDPSink,PulseAudioRDPSource}` sockets.

In order to use them, simply uncomment lines in [docker-compose.yaml](docker-compose.yaml) starting with `# WSL2` (for the player container) and run again `docker compose up -d`.

#### Manual check

After running

```shell
docker exec -it player python -c "import miniaudio; print(miniaudio.Devices().get_playbacks())"
```

you should see at least one audio sink, e.g.

```python
[{'name': 'RDP Sink', 'type': <DeviceType.PLAYBACK: 1>, 'id': <cdata 'union ma_device_id *' owning 256 bytes>, 
'formats': [{'format': '16-bit Signed Integer', 'samplerate': 44100, 'channels': 2}]}]
```

If so,

```shell
docker exec -it player python play_sample.py
```

should play music to your ears!

### Configuration

Configuration files ([backend](backend/config.yaml), [player](player/config.yaml)) are mounted from the host so should be edited on the host.  
They have schema declared for them so feel free to play around in any code editor supporting provided schema for yaml files.

#### Offset

The computer on which the player is running may not be precisely synchronised with the expected start of the break and thus the music playback.  
If, for this or any other reason, you need to move the start of the interval by a few or several seconds, simply edit the `breaks.offset.seconds` parameter in the [player/config.yaml](player/config.yaml) according to the rule

> program time is actual time plus offset (positive or negative)
