package com.dzerain.tarea2.controller;

import com.dzerain.tarea2.dto.Usuario;
import com.dzerain.tarea2.service.UserServices;
import java.util.List;
import java.util.Optional;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/user")
public class UserController {
  private final UserServices userServices;

  public UserController(UserServices userServices) {
    this.userServices = userServices;
  }

  @GetMapping("/list")
  public List<Usuario> list() {
    return userServices.list();
  }

  @GetMapping("/{id}")
  public Usuario getUser(@PathVariable Integer id) {
      Optional<Usuario>usuario= userServices.getUser(id);
      return usuario.orElse(null);
  }
}
