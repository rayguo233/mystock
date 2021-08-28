#!/usr/bin/env bash

export DJANGO_SETTINGS_MODULE=mystock_backend.dev_settings
head=python3\ manage.py
case $1 in
   p)
      brew services start postgresql
      ;;
   r)
      $head runserver "${@:2}"
      ;;
   m)
      $head migrate "${@:2}"
      ;;
   mm)
      $head makemigrations "${@:2}"
      ;;
   mm-all)
      $head makemigrations course user
      ;;
   rm-mm-all)
      echo Are you sure you want to remove all migrations?? [Y/n]
      read answer
      case $answer in
         Y)
            echo deleting all migrations
            rm -rf **/migrations
            ;;
         n)
            echo okay you gave up
            ;;
         *)
            echo invalid answer, please input Y or n
            ;;
      esac
esac