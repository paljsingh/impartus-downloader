import pytest


@pytest.fixture
def m3u8_sample():
    return """
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-ALLOW-CACHE:YES
#EXT-X-TARGETDURATION:62
#EXT-X-KEY:METHOD=AES-128,URI=\"http://a.impartus.com/api/fetchvideo/getVideoKey?ttid=4168424&keyid=0\"
#EXTINF:10.276278,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0000_hls_0.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0001_hls_0.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0002_hls_0.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0003_hls_0.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0004_hls_0.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0005_hls_0.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0006_hls_0.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0007_hls_0.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0008_hls_0.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0009_hls_0.ts
#EXT-X-KEY:METHOD=AES-128,URI=\"http://a.impartus.com/api/fetchvideo/getVideoKey?ttid=4168424&keyid=1\"
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0010_hls_1.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0011_hls_1.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0012_hls_1.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0013_hls_1.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0014_hls_1.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0015_hls_1.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0016_hls_1.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0017_hls_1.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0018_hls_1.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0019_hls_1.ts
#EXT-X-KEY:METHOD=AES-128,URI=\"http://a.impartus.com/api/fetchvideo/getVideoKey?ttid=4168424&keyid=2\"
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0020_hls_2.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0021_hls_2.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0022_hls_2.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0023_hls_2.ts
#EXTINF:9.800000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0024_hls_2.ts
#EXTINF:10.920000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0025_hls_2.ts
#EXTINF:9.920000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0026_hls_2.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0027_hls_2.ts
#EXTINF:9.640000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0028_hls_2.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0029_hls_2.ts
#EXT-X-KEY:METHOD=AES-128,URI=\"http://a.impartus.com/api/fetchvideo/getVideoKey?ttid=4168424&keyid=3\"
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0030_hls_3.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0031_hls_3.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0032_hls_3.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0033_hls_3.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0034_hls_3.ts
#EXTINF:9.920000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0035_hls_3.ts
#EXTINF:9.960000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0036_hls_3.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0037_hls_3.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0038_hls_3.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0039_hls_3.ts
#EXT-X-KEY:METHOD=AES-128,URI=\"http://a.impartus.com/api/fetchvideo/getVideoKey?ttid=4168424&keyid=4\"
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0040_hls_4.ts
#EXTINF:9.640000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0041_hls_4.ts
#EXTINF:10.840000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0042_hls_4.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0043_hls_4.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0044_hls_4.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0045_hls_4.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0046_hls_4.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0047_hls_4.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0048_hls_4.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0049_hls_4.ts
#EXT-X-KEY:METHOD=AES-128,URI=\"http://a.impartus.com/api/fetchvideo/getVideoKey?ttid=4168424&keyid=5\"
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0050_hls_5.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0051_hls_5.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0052_hls_5.ts
#EXTINF:10.040000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0053_hls_5.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0054_hls_5.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0055_hls_5.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0056_hls_5.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0057_hls_5.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0058_hls_5.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0059_hls_5.ts
#EXT-X-KEY:METHOD=AES-128,URI=\"http://a.impartus.com/api/fetchvideo/getVideoKey?ttid=4168424&keyid=6\"
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0060_hls_6.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0061_hls_6.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0062_hls_6.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0063_hls_6.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0064_hls_6.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0065_hls_6.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0066_hls_6.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0067_hls_6.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0068_hls_6.ts
#EXTINF:10.000000,
https://impartusmedia.oss-ap-south-1.aliyuncs.com/download1/4168424_hls/854x480_30/854x480_30v1_0069_hls_6.t
""".splitlines()


def test_init(mocker, m3u8_sample):
    from lib.media.m3u8parser import M3u8Parser

    # with no parameters
    m3u8parser = M3u8Parser()
    assert len(m3u8parser.m3u8_content) == 0
    assert m3u8parser.summary == {}
    assert m3u8parser.tracks == [[]]

    # with content list
    m3u8parser = M3u8Parser(m3u8_sample)
    assert m3u8parser.m3u8_content == m3u8_sample
    assert m3u8parser.summary == {}
    assert m3u8parser.tracks == [[]]

    # with tracks
    m3u8parser = M3u8Parser(m3u8_sample, num_tracks=3)
    assert m3u8parser.m3u8_content == m3u8_sample
    assert m3u8parser.summary == {}
    assert m3u8parser.tracks == [[], [], []]


def test_parse(mocker, m3u8_sample):
    from lib.media.m3u8parser import M3u8Parser

    # with no parameters
    summary_object, tracks_object = M3u8Parser().parse()
    assert summary_object == {
            "key_files": 0,
            "media_files": 0,
            "total_files": 0,
            "total_duration": 0,
        }
    assert tracks_object == [[]]

    # with content list
    summary_object, tracks_object = M3u8Parser(m3u8_sample).parse()
    assert summary_object == {
            "key_files": 7,
            "media_files": 70,
            "total_files": 77,
            "total_duration": 701,
        }
    assert len(tracks_object) == 1          # single track
    assert len(tracks_object[0]) == 70      # 70 media files.

    # with tracks
    summary_object, tracks_object = M3u8Parser(m3u8_sample, num_tracks=3).parse()
    assert summary_object == {
            "key_files": 7,
            "media_files": 70,
            "total_files": 77,
            "total_duration": 701,
        }
    assert len(tracks_object) == 3          # 3 tracks
    assert len(tracks_object[0]) == 70      # 70 media files in track 0.
    assert len(tracks_object[1]) == 0       # 0 media files in track 1.
    assert len(tracks_object[2]) == 0       # 0 media files in track 2.
