from similarity_engine import similarity_matrices
from expertise_matcher import expertise_difference_mask

the expertise difference mask is a dictionary where key values are the 
mapping of mentee expertise areas to mentor expertise areas
as:
mentee_area_0_to_mentor_area_0: //2D arrary containing boolean values if their expertise level are matched or not
mentee_area_0_to_mentor_area_1
mentee_area_0_to_mentor_area_2


mentee_area_1_to_mentor_area_0
mentee_area_1_to_mentor_area_1
mentee_area_1_to_mentor_area_2



mentee_area_2_to_mentor_area_0
mentee_area_2_to_mentor_area_1
mentee_area_2_to_mentor_area_2

similarity_matrices: a dictionary where key values are the 
mapping of mentee interest areas to mentor interest area areas
higher the value,higher the mentor has the same experience the mentee is seeking to imprve
as:
mentee_area_0_to_mentor_area_0: //2D arrary containing float values determining the experience/interest simlairty of mentors and mentees
mentee_area_0_to_mentor_area_1
mentee_area_0_to_mentor_area_2


mentee_area_1_to_mentor_area_0
mentee_area_1_to_mentor_area_1
mentee_area_1_to_mentor_area_2



mentee_area_2_to_mentor_area_0
mentee_area_2_to_mentor_area_1
mentee_area_2_to_mentor_area_2


i want the expertise_difference_mask too be used to create a similar dict to give score to each pair
for their compatibility. suggest me some ways in which i can implement this so that i can generate meentor mentee matches based on 
interest areas and experience level. i want all mentees to have at least one mentor, and all mentees to have at least one mentee_area_0_to_mentor_area_0
ideally each mentor/mentee should be paired with 1(min)-3(max) mentee/mentors respectively