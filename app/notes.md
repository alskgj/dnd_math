original:
=========
<div class="form-row">
      
	  <div class="form-group "><label class="control-label" for="attacks-0-sub_attacks-0-attack">Attack</label>
        	  <input class="form-control" id="attacks-0-sub_attacks-0-attack" name="attacks-0-sub_attacks-0-attack" type="text" value="3d4+1">
	  </div>

	  <div class="form-group "><label class="control-label" for="attacks-0-sub_attacks-1-attack">Attack</label>
        	  <input class="form-control" id="attacks-0-sub_attacks-1-attack" name="attacks-0-sub_attacks-1-attack" type="text" value="+4 3d8">
	  </div>

</div>

proposed:
========

<div class="form-row">
      
	  <div class="form-group col-md-6">
        	  <input class="form-control" id="attacks-0-sub_attacks-0-attack" name="attacks-0-sub_attacks-0-attack" type="text" value="3d4+1">
	  </div>

	  <div class="form-group col-md-6">
        	  <input class="form-control" id="attacks-0-sub_attacks-1-attack" name="attacks-0-sub_attacks-1-attack" type="text" value="+4 3d8">
	  </div>

</div>



bootstrap:
==========

  <div class="form-row">
    <div class="form-group col-md-6">
      <label for="inputEmail4">Email</label>
      <input type="email" class="form-control" id="inputEmail4" placeholder="Email">
    </div>
    <div class="form-group col-md-6">
      <label for="inputPassword4">Password</label>
      <input type="password" class="form-control" id="inputPassword4" placeholder="Password">
    </div>
  </div>


button:
=======
was: <input class="btn btn-primary" id="attack_submit" name="attack_submit" type="submit" value="Attack">
from: {{ wtf.form_field(form.attack_submit, class="btn btn-primary") }}