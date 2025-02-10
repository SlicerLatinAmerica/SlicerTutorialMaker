#-----------------------------------------------------------------------------
set(MODULE_NAME TutorialMaker)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  Lib/Anotations.py
  Lib/CreateTutorial.py
  Lib/FileMDHTML.py
  Lib/GitTools.py
  Lib/painter.py
  Lib/tmLabel.py
  Lib/TutorialEditor.py
  Lib/TutorialGUI.py
  Lib/utils.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
  Resources/UI/${MODULE_NAME}.ui
  Resources/Icons/Painter/click_icon.png
  Resources/Icons/Painter/line_down.png
  Resources/Icons/Painter/line_top.png
  Resources/Icons/Painter/slicer.png
  Resources/Icons/ScreenshotAnnotator/act1.png
  Resources/Icons/ScreenshotAnnotator/act1_p.png
  Resources/Icons/ScreenshotAnnotator/act2.png
  Resources/Icons/ScreenshotAnnotator/act2_p.png
  Resources/Icons/ScreenshotAnnotator/act3.png
  Resources/Icons/ScreenshotAnnotator/act3_p.png
  Resources/Icons/ScreenshotAnnotator/act4.png
  Resources/Icons/ScreenshotAnnotator/act4_p.png
  Resources/Icons/ScreenshotAnnotator/act5.png
  Resources/Icons/ScreenshotAnnotator/act5_p.png
  Resources/Icons/ScreenshotAnnotator/add.png
  Resources/Icons/ScreenshotAnnotator/arrow.png
  Resources/Icons/ScreenshotAnnotator/back.png
  Resources/Icons/ScreenshotAnnotator/cancel.png
  Resources/Icons/ScreenshotAnnotator/clean.png
  Resources/Icons/ScreenshotAnnotator/color.png
  Resources/Icons/ScreenshotAnnotator/copy.png
  Resources/Icons/ScreenshotAnnotator/del.png
  Resources/Icons/ScreenshotAnnotator/fill_p.png
  Resources/Icons/ScreenshotAnnotator/fill_u.png
  Resources/Icons/ScreenshotAnnotator/icon_p.png
  Resources/Icons/ScreenshotAnnotator/image.png
  Resources/Icons/ScreenshotAnnotator/NewGUI.png
  Resources/Icons/ScreenshotAnnotator/open.png
  Resources/Icons/ScreenshotAnnotator/pointer.png
  Resources/Icons/ScreenshotAnnotator/pointer_p.png
  Resources/Icons/ScreenshotAnnotator/remove.png
  Resources/Icons/ScreenshotAnnotator/save.png
  Resources/Icons/ScreenshotAnnotator/selec.png
  Resources/Icons/ScreenshotAnnotator/selec_p.png
  Resources/Icons/ScreenshotAnnotator/size.png
  Resources/NewSlide/cover_page.png
  Resources/NewSlide/white.png
  Resources/UI/CreateNewTutorial.ui
  Resources/UI/ScreenshotAnnotator.ui
  Resources/UI/TutorialEditor.ui
  Resources/UI/WidgetAnnotator.ui
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # Register the unittest subclass in the main script as a ctest.
  # Note that the test will also be available at runtime.
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # Additional build-time testing
  add_subdirectory(Testing)
endif()
