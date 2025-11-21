OBS_PROJECT := EA4
OBS_PACKAGE := ea-ruby27-passenger
DISABLE_BUILD := repository=CentOS_6.5_standard repository=CentOS_7 repository=CentOS_9 repository=Almalinux_10
include $(EATOOLS_BUILD_DIR)obs.mk
