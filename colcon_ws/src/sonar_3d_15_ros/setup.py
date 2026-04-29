from setuptools import setup

package_name = "sonar_3d_15_ros"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", [
            "launch/sonar_setup_and_publish.launch.py",
        ]),
        ("share/" + package_name, [
            "sonar_3d_15_ros/sonar-3d-15-protocol.proto",
        ]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="TODO",
    maintainer_email="TODO@example.com",
    description="ROS 2 wrapper for Water Linked Sonar 3D-15 setup and data processing.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "sonar_3d_api=sonar_3d_15_ros.interface_sonar_api:main",
            "sonar_3d_save=sonar_3d_15_ros.save_sonar_data:main",
            "sonar_3d_inspect=sonar_3d_15_ros.inspect_sonar_data:main",
            "sonar_3d_setup_publish=sonar_3d_15_ros.sonar_setup_and_publish:main",
        ],
    },
)
