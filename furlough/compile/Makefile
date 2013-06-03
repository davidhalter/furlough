BOOTSTRAP = ../assets/css/bootstrap.css
BOOTSTRAP_LESS = bootstrap.less
JS_DIR = ../assets/js/bootstrap/
CHECK=\033[32m✔\033[39m
HR=\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#

custom: 
	@echo "\n${HR}"
	@echo "Building Bootstrap with Custom Extensions (bootstrap.css)"
	@echo "${HR}\n"
	recess --compile ${BOOTSTRAP_LESS} > ${BOOTSTRAP}
	@echo "Compiling LESS with Recess...               ${CHECK} Done\n"

js:
	@echo "\n${HR}"
	@echo "Copying Javascript to ${JS_DIR}"
	@echo "${HR}\n"
	cp bootstrap/js/*.js ${JS_DIR}
	@echo ".............................               ${CHECK} Done\n"

watch:
	echo "Watching less files..."; \
	watchr -e "watch('.*\.less') { system 'make' }"

