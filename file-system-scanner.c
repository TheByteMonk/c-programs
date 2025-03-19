/* File System Scanner and Analyzer

Features
  - Recursive directory traveral
  - File metadata analysis
  - File type detection
  - Size statistics
  - Access time analysis
  - Data visualization in terminal
  - Custom filtering options
  - Report generation
 
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
