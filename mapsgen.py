import staticmaps
from iplocate import selfpath

# context.set_tile_provider(staticmaps.tile_provider_ArcGISWorldImagery)
# context.set_tile_provider(staticmaps.tile_provider_CartoDarkNoLabels)
cntxt200 = staticmaps.Context()
cntxt200.set_tile_provider(staticmaps.tile_provider_OSM)
cntxt300 = staticmaps.Context()
cntxt300.set_tile_provider(staticmaps.tile_provider_OSM)
cntxtAll = staticmaps.Context()
cntxtAll.set_tile_provider(staticmaps.tile_provider_OSM)


def map200(geolocs):
    for loc in geolocs:
        lat = float(loc[0].split(',')[0])
        lon = float(loc[0].split(',')[1])
        marca200 = staticmaps.create_latlng(lat, lon)
        cntxt200.add_object(
            staticmaps.Marker(
                marca200,
                color=staticmaps.parse_color('#00ff29'),
                size=4
            )
        )

    svg_image = cntxt200.render_svg(1920, 1080)
    with open(f"{selfpath}/maps/map_200.svg", "w", encoding="utf-8") as f:
        svg_image.write(f, pretty=True)

    image = cntxt200.render_cairo(1920, 1080)
    image.write_to_png(f"{selfpath}/maps/map_200.png")


def map300(geolocs):
    for loc in geolocs:
        lat = float(loc[0].split(',')[0])
        lon = float(loc[0].split(',')[1])
        marca300 = staticmaps.create_latlng(lat, lon)
        cntxt300.add_object(staticmaps.Marker(
            marca300, color=staticmaps.parse_color('#b20101'), size=3))

    svg_image = cntxt300.render_svg(1920, 1080)
    with open(f"{selfpath}/maps/map_300.svg", "w", encoding="utf-8") as f:
        svg_image.write(f, pretty=True)

    image = cntxt300.render_cairo(1920, 1080)
    image.write_to_png(f"{selfpath}/maps/map_300.png")


def maps_gen(locs_200, locs_300):
    maps_thumbs(locs_200, locs_300)
    map200(locs_200)
    map300(locs_300)
    for loc in locs_300:
        lat = float(loc[0].split(',')[0])
        lon = float(loc[0].split(',')[1])
        marca3 = staticmaps.create_latlng(lat, lon)
        cntxtAll.add_object(
            staticmaps.Marker(
                marca3,
                color=staticmaps.parse_color('#b20101'),
                size=3
            )
        )

    for loc in locs_200:
        lat = float(loc[0].split(',')[0])
        lon = float(loc[0].split(',')[1])
        marca3 = staticmaps.create_latlng(lat, lon)
        cntxtAll.add_object(
            staticmaps.Marker(
                marca3,
                color=staticmaps.parse_color('#00ff29'),
                size=4
            )
        )

    svg_image = cntxtAll.render_svg(1920, 1080)
    with open(f"{selfpath}/maps/map_all.svg", "w", encoding="utf-8") as f:
        svg_image.write(f, pretty=True)

    image = cntxtAll.render_cairo(1920, 1080)
    image.write_to_png(f"{selfpath}/maps/map_all.png")
    maps_thumbs(locs_200, locs_300)


def maps_thumbs(locs_200, locs_300):
    cntxtdemo = staticmaps.Context()
    cntxtdemo.set_tile_provider(staticmaps.tile_provider_OSM)

    for loc in locs_300:
        lat = float(loc[0].split(',')[0])
        lon = float(loc[0].split(',')[1])
        demo300 = staticmaps.create_latlng(lat, lon)
        cntxtdemo.add_object(
            staticmaps.Marker(
                demo300,
                color=staticmaps.parse_color('#b20101'),
                size=3
            )
        )

    for loc in locs_200:
        lat = float(loc[0].split(',')[0])
        lon = float(loc[0].split(',')[1])
        demo200 = staticmaps.create_latlng(lat, lon)
        cntxtdemo.add_object(
            staticmaps.Marker(
                demo200,
                color=staticmaps.parse_color('#00ff29'),
                size=3.5
            )
        )

    svg_thumb = cntxtdemo.render_svg(1024, 768)
    with open(f"{selfpath}/maps/map_thumb.svg", "w", encoding="utf-8") as f:
        svg_thumb.write(f, pretty=True)

    image = cntxtdemo.render_cairo(1024, 768)
    image.write_to_png(f"{selfpath}/maps/map_thumb.png")
