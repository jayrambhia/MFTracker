from setuptools import setup, find_packages

setup(name="mftracker",
    version = 0.1,
    download_url = "https://github.com/jayrambhia/MFTracker/downloads/tarball/master",
    description = "Median Flow Tracker using SimpleCV and OpenCV",
    keywords = "opencv, cv, simplecv, opentld, tracking, median flow, lucas kanede",
    author = "Jay Rambhia",
    author_email = "jayrambhia777@gmail.com",
    license = 'BSD',
    packages = find_packages(),
    requires = ["cv2","cv","simplecv"]
    )
